use dotenv::dotenv;
use std::{env, time};
use log::{error, info};
use simple_logger;
use tokio::time::sleep;
use crate::database::InsertErrors;
use crate::ppd::db_ops::insert_ppd_data;

mod database;
mod config;
mod ppd;
mod querys;
mod epc;

#[tokio::main]
async fn main() {
    simple_logger::init_with_level(log::Level::Info).unwrap();
    dotenv().ok();

    let config = config::Config{
        database_url: env::var("DATABASE_URL").unwrap(),
    };


    let mut database = database::HouseStatsDatabase::new(config).await.unwrap();

    // epc::epc_data::load_epc("data/all-domestic-certificates", &mut database).await.unwrap();


    // loop {
    //     info!("Checking for updates...");
    //     let new_sales = ppd::ppd_data::check_for_update(database.last_ppd_file).await.unwrap();
    //     if new_sales != String::new() {
    //         info!("New PPD data found");
    //         info!("Updating database...");
    //         match insert_ppd_data(&mut database, &new_sales).await {
    //             Ok(_) => {}
    //             Err(InsertErrors::PostgresError(e)) => {error!("Unable to update PPD data - {}", e);}
    //             Err(InsertErrors::CsvError(e)) => {error!("Unable to update PPD data - {}", e);}
    //         };
    //     }
    //
    //     info!("Waiting 1hr before checking again...");
    //     sleep(time::Duration::from_hours(1)).await;
    // }


}
