use crate::database::{HouseStatsDatabase, InsertErrors};
use crate::ppd::common::{HouseRow, PostcodeRow, SaleRow};
use crate::ppd::ppd_data::{PpdCsvRow, normalise_record_list};
use log::info;
use sha2::{Digest, Sha256};
use std::time::SystemTime;

pub async fn insert_ppd_data(
    database: &mut HouseStatsDatabase,
    ppd_data: &str,
) -> Result<(), InsertErrors> {
    let mut csv_reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_reader(ppd_data.as_bytes());

    let rows: Vec<PpdCsvRow> = match csv_reader.deserialize().collect::<Result<_, _>>() {
        Ok(rows) => rows,
        Err(e) => return Err(InsertErrors::CsvError(e)),
    };

    let (additions, _deletions) = normalise_record_list(rows);

    info!("Inserting ppd data");
    match batch_insert(database, additions).await {
        Ok(rows) => rows,
        Err(e) => return Err(InsertErrors::PostgresError(e)),
    };

    // TODO add deletion handling

    match database
        .set_new_ppd_update(Sha256::digest(ppd_data.as_bytes()))
        .await
    {
        Ok(rows) => rows,
        Err(e) => return Err(InsertErrors::PostgresError(e)),
    };

    Ok(())
}

async fn batch_insert_postcodes(
    tx: &tokio_postgres::Transaction<'_>,
    rows: Vec<PostcodeRow>,
) -> Result<(), tokio_postgres::Error> {
    let postcodes: Vec<&str> = rows.iter().map(|r| r.postcode.as_str()).collect();
    let streets: Vec<&str> = rows.iter().map(|r| r.street.as_str()).collect();
    let towns: Vec<&str> = rows.iter().map(|r| r.town.as_str()).collect();
    let districts: Vec<&str> = rows.iter().map(|r| r.district.as_str()).collect();
    let counties: Vec<&str> = rows.iter().map(|r| r.county.as_str()).collect();
    let outcodes: Vec<&str> = rows.iter().map(|r| r.outcode.as_str()).collect();
    let areas: Vec<&str> = rows.iter().map(|r| r.area.as_str()).collect();
    let sectors: Vec<&str> = rows.iter().map(|r| r.sector.as_str()).collect();

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
            &postcodes, &streets, &towns, &districts, &counties, &outcodes, &areas, &sectors,
        ],
    )
    .await?;
    Ok(())
}

async fn batch_insert_houses(
    tx: &tokio_postgres::Transaction<'_>,
    rows: &[HouseRow],
) -> Result<(), tokio_postgres::Error> {
    let houseids: Vec<&str> = rows.iter().map(|r| r.houseid.as_str()).collect();
    let paons: Vec<&str> = rows.iter().map(|r| r.paon.as_str()).collect();
    let saons: Vec<&str> = rows.iter().map(|r| r.saon.as_str()).collect();
    let postcodes: Vec<&str> = rows.iter().map(|r| r.postcode.as_str()).collect();
    let types: Vec<&str> = rows.iter().map(|r| r.property_type.as_str()).collect();

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
        &[&houseids, &paons, &saons, &postcodes, &types],
    )
    .await?;

    Ok(())
}

async fn batch_insert_sales(
    tx: &tokio_postgres::Transaction<'_>,
    rows: &[SaleRow],
) -> Result<(), tokio_postgres::Error> {
    let tuis: Vec<&str> = rows.iter().map(|r| r.tui.as_str()).collect();
    let prices: Vec<i32> = rows.iter().map(|r| r.price as i32).collect();

    let dates: Vec<SystemTime> = rows.iter().map(|r| SystemTime::from(r.date)).collect();

    let new_builds: Vec<bool> = rows.iter().map(|r| r.new_build).collect();
    let freeholds: Vec<bool> = rows.iter().map(|r| r.freehold).collect();

    let ppd_cats: Vec<&str> = rows.iter().map(|r| r.ppd_cat.as_str()).collect();

    let houseids: Vec<&str> = rows.iter().map(|r| r.houseid.as_str()).collect();

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

async fn batch_insert(
    database: &mut HouseStatsDatabase,
    rows: Vec<(PostcodeRow, HouseRow, SaleRow)>,
) -> Result<(), tokio_postgres::Error> {
    for chunk in rows.chunks(1000) {
        let tx = database.db_client.transaction().await?;

        let mut postcodes = Vec::with_capacity(chunk.len());
        let mut houses = Vec::with_capacity(chunk.len());
        let mut sales = Vec::with_capacity(chunk.len());

        for (p, h, s) in chunk {
            postcodes.push(p.clone());
            houses.push(h.clone());
            sales.push(s.clone());
        }

        batch_insert_postcodes(&tx, postcodes).await?;
        batch_insert_houses(&tx, &houses).await?;
        batch_insert_sales(&tx, &sales).await?;

        tx.commit().await?;
    }

    Ok(())
}
