use std::time::SystemTime;
use chrono::{DateTime, Utc};
use sha2::{Digest, Sha256};
use tokio_postgres::{NoTls};
use tokio::task::JoinHandle;
use log::{error, info};

use crate::common::{HouseRow, PostcodeRow, SaleRow};
use crate::config;
use crate::ppd_data::{download_all_ppd, normalise_record_list, PpdCsvRow};
use crate::querys::{CREATE_CONFIG_TABLE_QUERY, CREATE_HOUSES_TABLE_QUERY, CREATE_POSTCODE_TABLE_QUERY, CREATE_SALE_TABLE_QUERY};

pub struct HouseStatsDatabase {
    db_client: tokio_postgres::Client,
    _db_conn_routine: JoinHandle<()>,
    pub last_init_data: DateTime<Utc>,

    pub last_ppd_update: DateTime<Utc>,
    pub last_ppd_file: crypto_common::Output<Sha256>,

    pub last_epc_update: DateTime<Utc>,
    pub last_epc_file: crypto_common::Output<Sha256>,

    pub last_linking_run: DateTime<Utc>,
}

#[derive(Debug)]
pub enum InsertErrors {
    CsvError(csv::Error),
    PostgresError(tokio_postgres::Error)
}

impl HouseStatsDatabase {
    pub async fn new(config: config::Config) -> Result<HouseStatsDatabase, tokio_postgres::Error> {

        let (client, connection) = tokio_postgres::connect(
            config.database_url.as_str(),
            NoTls).await?;

        let conn_coroutine = tokio::spawn(async move {
            if let Err(e) = connection.await {
                error!("connection error: {}", e);
            }
        });

        let mut db = HouseStatsDatabase {
            db_client: client,
            _db_conn_routine: conn_coroutine,
            last_ppd_update: Default::default(),
            last_ppd_file: Default::default(),
            last_epc_update: Default::default(),
            last_epc_file: Default::default(),

            last_linking_run: Default::default(),
            last_init_data: Default::default(),
        };

        match db.sync_db().await {
            Ok(_) => {info!("Database successfully synced")},
            Err(_e) => {
                info!("Database has not been initialised");
                info!("Initialising database");
                db.init_db().await?;
                info!("Database table initialisation completed");
            }
        };

        Ok(db)

    }

    async fn sync_db(&mut self) -> Result<(), tokio_postgres::Error> {
        let row_result = self.db_client
            .query_one("SELECT * FROM config;", &[])
            .await;

        let row = match row_result {
            Ok(row) => row,
            Err(e) => return Err(e),
        };

        self.last_ppd_update = DateTime::from(row.get::<usize, SystemTime>(1));
        self.last_ppd_file = *crypto_common::Output::<Sha256>::from_slice(row.get::<usize, &[u8]>(2));

        self.last_epc_update = DateTime::from(row.get::<usize, SystemTime>(3));
        self.last_epc_file = *crypto_common::Output::<Sha256>::from_slice(row.get::<usize, &[u8]>(4));

        self.last_linking_run = DateTime::from(row.get::<usize, SystemTime>(5));
        self.last_init_data = DateTime::from(row.get::<usize, SystemTime>(6));

        Ok(())
    }

    async fn init_db(&mut self) -> Result<(), tokio_postgres::Error> {
        info!("Initialising database tables");
        self.db_client.execute(CREATE_CONFIG_TABLE_QUERY, &[]).await?;
        self.db_client.batch_execute(CREATE_POSTCODE_TABLE_QUERY).await?;
        self.db_client.batch_execute(CREATE_HOUSES_TABLE_QUERY).await?;
        self.db_client.batch_execute(CREATE_SALE_TABLE_QUERY).await?;

        info!("Adding data to config table");
        self.db_client.execute("INSERT INTO config
                             (last_ppd_update, last_ppd_file, last_epc_update, last_epc_file,
                              last_linking_run, last_init_data)
                             VALUES ($1, $2, $3, $4, $5, $6);",
            &[
                &SystemTime::from(self.last_ppd_update),
                &self.last_ppd_file.as_slice(),
                &SystemTime::from(self.last_epc_update),
                &self.last_epc_file.as_slice(),
                &SystemTime::from(self.last_linking_run),
                &SystemTime::from(self.last_init_data),
            ],
        ).await?;

        // TODO fix error handling here
        let all_ppd = download_all_ppd().await.unwrap();
        info!("Inserting all PPD rows");
        self.insert_ppd_data(&all_ppd).await.unwrap();



        Ok(())
    }

    pub async fn set_new_ppd_update(&mut self, hash: crypto_common::Output<Sha256>) -> Result<(), tokio_postgres::Error> {
        self.db_client.execute(
            "UPDATE config SET last_ppd_update = $1, last_ppd_file = $2;",
            &[&SystemTime::now(), &hash.as_slice()],
        ).await?;

        Ok(())
    }

    pub async fn insert_ppd_data(&mut self, ppd_data: &String) -> Result<(), InsertErrors> {
        let mut csv_reader = csv::ReaderBuilder::new()
            .has_headers(false)
            .from_reader(ppd_data.as_bytes());

        let rows: Vec<PpdCsvRow> = match csv_reader.deserialize().collect::<Result<_, _>>() {
            Ok(rows) => rows,
            Err(e) => return Err(InsertErrors::CsvError(e)),
        };

        let (additions, _deletions) = normalise_record_list(rows);

        info!("Inserting ppd data");
        match self.batch_insert(additions).await {
            Ok(rows) => rows,
            Err(e) => return Err(InsertErrors::PostgresError(e)),
        };

        // TODO add deletion handling

        match self.set_new_ppd_update(Sha256::digest(ppd_data)).await {
            Ok(rows) => rows,
            Err(e) => return Err(InsertErrors::PostgresError(e)),
        };

        Ok(())
    }

    async fn batch_insert_postcodes(tx: &tokio_postgres::Transaction<'_>, rows: Vec<PostcodeRow>) -> Result<(), tokio_postgres::Error> {
        let postcodes: Vec<&str> = rows.iter().map(|r| r.postcode.as_str()).collect();
        let streets:   Vec<&str> = rows.iter().map(|r| r.street.as_str()).collect();
        let towns:     Vec<&str> = rows.iter().map(|r| r.town.as_str()).collect();
        let districts: Vec<&str> = rows.iter().map(|r| r.district.as_str()).collect();
        let counties:  Vec<&str> = rows.iter().map(|r| r.county.as_str()).collect();
        let outcodes:  Vec<&str> = rows.iter().map(|r| r.outcode.as_str()).collect();
        let areas:     Vec<&str> = rows.iter().map(|r| r.area.as_str()).collect();
        let sectors:   Vec<&str> = rows.iter().map(|r| r.sector.as_str()).collect();

        tx.execute(
            "
        INSERT INTO postcodes (
            postcode, street, town, district, county,
            outcode, area, sector
        )
        SELECT * FROM UNNEST(
            $1::TEXT[], $2::TEXT[], $3::TEXT[], $4::TEXT[],
            $5::TEXT[], $6::TEXT[], $7::TEXT[], $8::TEXT[]
        )
        ON CONFLICT (postcode) DO NOTHING",
            &[
                &postcodes, &streets, &towns, &districts,
                &counties, &outcodes, &areas, &sectors,
            ],
        ).await?;
        Ok(())
    }

    async fn batch_insert_houses(
        tx: &tokio_postgres::Transaction<'_>,
        rows: &[HouseRow],
    ) -> Result<(), tokio_postgres::Error> {

        let houseids: Vec<&str>  = rows.iter().map(|r| r.houseid.as_str()).collect();
        let paons:    Vec<&str>  = rows.iter().map(|r| r.paon.as_str()).collect();
        let saons:    Vec<&str>  = rows.iter().map(|r| r.saon.as_str()).collect();
        let postcodes: Vec<&str> = rows.iter().map(|r| r.postcode.as_str()).collect();
        let types: Vec<&str> = rows
            .iter()
            .map(|r| r.property_type.as_str())
            .collect();

        tx.execute(
            "
        INSERT INTO houses (
            houseid, paon, saon, postcode, type
        )
        SELECT * FROM UNNEST(
            $1::VARCHAR[],
            $2::VARCHAR[],
            $3::VARCHAR[],
            $4::VARCHAR[],
            $5::CHAR[]
        )
        ON CONFLICT (houseid) DO NOTHING
        ",
            &[
                &houseids,
                &paons,
                &saons,
                &postcodes,
                &types,
            ],
        ).await?;

        Ok(())
    }

    async fn batch_insert_sales(
        tx: &tokio_postgres::Transaction<'_>,
        rows: &[SaleRow],
    ) -> Result<(), tokio_postgres::Error> {

        let tuis: Vec<&str> = rows.iter().map(|r| r.tui.as_str()).collect();
        let prices: Vec<i32> = rows.iter().map(|r| r.price as i32).collect();

        let dates: Vec<SystemTime> =
            rows.iter().map(|r| SystemTime::from(r.date)).collect();

        let new_builds: Vec<bool> = rows.iter().map(|r| r.new_build).collect();
        let freeholds: Vec<bool> = rows.iter().map(|r| r.freehold).collect();

        let ppd_cats: Vec<&str> =
            rows.iter().map(|r| r.ppd_cat.as_str()).collect();

        let houseids: Vec<&str> =
            rows.iter().map(|r| r.houseid.as_str()).collect();


        tx.execute(
            "
        INSERT INTO sales (
            tui, price, date, new, freehold, ppd_cat, houseid
        )
        SELECT * FROM UNNEST(
            $1::VARCHAR[],
            $2::INTEGER[],
            $3::TIMESTAMPTZ[],
            $4::BOOLEAN[],
            $5::BOOLEAN[],
            $6::CHAR[],
            $7::VARCHAR[]
        )
        ON CONFLICT (tui) DO NOTHING",
            &[
                &tuis,
                &prices,
                &dates,
                &new_builds,
                &freeholds,
                &ppd_cats,
                &houseids,
            ],
        )
            .await?;

        Ok(())
    }

    async fn batch_insert(&mut self, rows: Vec<(PostcodeRow, HouseRow, SaleRow)>) -> Result<(), tokio_postgres::Error> {
        for chunk in rows.chunks(1000) {
            let tx = self.db_client.transaction().await?;

            let mut postcodes = Vec::with_capacity(chunk.len());
            let mut houses = Vec::with_capacity(chunk.len());
            let mut sales = Vec::with_capacity(chunk.len());

            for (p, h, s) in chunk {
                postcodes.push(p.clone());
                houses.push(h.clone());
                sales.push(s.clone());
            }

            HouseStatsDatabase::batch_insert_postcodes(&tx, postcodes).await?;
            HouseStatsDatabase::batch_insert_houses(&tx, &houses).await?;
            HouseStatsDatabase::batch_insert_sales(&tx, &sales).await?;

            tx.commit().await?;
        }

        Ok(())
    }

}
