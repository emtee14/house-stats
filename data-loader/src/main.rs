use dotenv::dotenv;
use std::{env, time};
use log::{error, info};
use simple_logger;
use tokio::time::sleep;
use crate::database::InsertErrors;
use crate::ppd_data::check_for_update;

mod database;
mod config;
mod querys;
mod ppd_data;
mod common;

#[tokio::main]
async fn main() {
    simple_logger::init_with_level(log::Level::Info).unwrap();
    dotenv().ok();

    let config = config::Config{
        database_url: env::var("DATABASE_URL").unwrap(),
    };


    let mut database = database::HouseStatsDatabase::new(config).await.unwrap();

    loop {



        info!("Checking for updates...");
        let new_sales = check_for_update(database.last_ppd_file).await.unwrap();
        if new_sales != String::new() {
            info!("New PPD data found");
            info!("Updating database...");
            match database.insert_ppd_data(&new_sales).await {
                Ok(_) => {}
                Err(InsertErrors::PostgresError(e)) => {error!("Unable to update PPD data - {}", e);}
                Err(InsertErrors::CsvError(e)) => {error!("Unable to update PPD data - {}", e);}
            };
        }

        info!("Waiting 1hr before checking again...");
        sleep(time::Duration::from_hours(1)).await;
    }


}
