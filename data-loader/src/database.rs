use chrono::{DateTime, Utc};
use log::{error, info};
use sha2::Sha256;
use std::time::SystemTime;
use tokio::task::JoinHandle;
use tokio_postgres::NoTls;

use crate::querys::{
    CREATE_CONFIG_TABLE_QUERY, CREATE_EPC_CERT_TABLE, CREATE_HOUSES_TABLE_QUERY,
    CREATE_POSTCODE_TABLE_QUERY, CREATE_SALE_TABLE_QUERY,
};
use crate::{config, ppd};
use ppd::common::{HouseRow, PostcodeRow, SaleRow};
use ppd::ppd_data::{PpdCsvRow, download_all_ppd, normalise_record_list};

pub struct HouseStatsDatabase {
    pub(crate) db_client: tokio_postgres::Client,
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
    PostgresError(tokio_postgres::Error),
}

impl HouseStatsDatabase {
    pub async fn new(config: config::Config) -> Result<HouseStatsDatabase, tokio_postgres::Error> {
        let (client, connection) =
            tokio_postgres::connect(config.database_url.as_str(), NoTls).await?;

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
            Ok(_) => {
                info!("Database successfully synced")
            }
            Err(_e) => {
                info!("Database has not been initialised");
                info!("Initialising database");
                db.init_db().await?;
                info!("Database table initialisation completed");
            }
        };

        let all_ppd = download_all_ppd().await.unwrap();
        info!("Inserting all PPD rows");
        ppd::db_ops::insert_ppd_data(&mut db, &all_ppd).await.unwrap();

        Ok(db)
    }

    async fn sync_db(&mut self) -> Result<(), tokio_postgres::Error> {
        let row_result = self.db_client
            .query_one("SELECT * FROM config;", &[]).await;

        let row = match row_result {
            Ok(row) => row,
            Err(e) => return Err(e),
        };

        self.last_ppd_update = DateTime::from(row.get::<usize, SystemTime>(1));
        self.last_ppd_file =
            *crypto_common::Output::<Sha256>::from_slice(row.get::<usize, &[u8]>(2));

        self.last_epc_update = DateTime::from(row.get::<usize, SystemTime>(3));
        self.last_epc_file =
            *crypto_common::Output::<Sha256>::from_slice(row.get::<usize, &[u8]>(4));

        self.last_linking_run = DateTime::from(row.get::<usize, SystemTime>(5));
        self.last_init_data = DateTime::from(row.get::<usize, SystemTime>(6));

        Ok(())
    }

    async fn init_db(&mut self) -> Result<(), tokio_postgres::Error> {
        info!("Initialising database tables");
        self.db_client
            .execute(CREATE_CONFIG_TABLE_QUERY, &[])
            .await?;

        // PPD
        self.db_client
            .batch_execute(CREATE_POSTCODE_TABLE_QUERY)
            .await?;
        self.db_client
            .batch_execute(CREATE_HOUSES_TABLE_QUERY)
            .await?;
        self.db_client
            .batch_execute(CREATE_SALE_TABLE_QUERY)
            .await?;

        // EPC
        self.db_client.batch_execute(CREATE_EPC_CERT_TABLE).await?;

        info!("Adding data to config table");
        self.db_client
            .execute(
                "INSERT INTO config
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
            )
            .await?;

        // TODO fix error handling here
        Ok(())
    }

    pub async fn set_new_ppd_update(
        &mut self,
        hash: crypto_common::Output<Sha256>,
    ) -> Result<(), tokio_postgres::Error> {
        self.db_client
            .execute(
                "UPDATE config SET last_ppd_update = $1, last_ppd_file = $2;",
                &[&SystemTime::now(), &hash.as_slice()],
            )
            .await?;

        Ok(())
    }
}
