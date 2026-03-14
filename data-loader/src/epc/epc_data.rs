use crate::database::{HouseStatsDatabase, InsertErrors};
use crate::epc::common::EpcCertRow;
use crate::epc::db_ops;
use indicatif::ProgressBar;
use log::info;
use std::path::PathBuf;
use walkdir::WalkDir;

pub async fn load_epc(
    filename: &str,
    house_stats_database: &mut HouseStatsDatabase,
) -> Result<(), InsertErrors> {
    let (cert_paths, rec_paths) = load_csv_paths(filename);

    info!("Reading EPC files");
    let pb = ProgressBar::new(cert_paths.len() as u64);
    for cert_path in cert_paths {
        let cert_rows = read_csv_cert_rows(cert_path);

        match cert_rows {
            Ok(cert_rows) => {
                match db_ops::insert_epc_cert(house_stats_database, &cert_rows).await {
                    Ok(_) => {}
                    Err(e) => return Err(InsertErrors::PostgresError(e)),
                }
            }
            Err(e) => return Err(InsertErrors::CsvError(e)),
        }
        pb.inc(1);
    }
    pb.finish_with_message("Inserted EPC files");

    Ok(())
}

fn load_csv_paths(filename: &str) -> (Vec<PathBuf>, Vec<PathBuf>) {
    info!("Finding EPC files");

    let mut certs = Vec::<PathBuf>::new();
    let mut recs = Vec::<PathBuf>::new();

    for entry in WalkDir::new(filename).into_iter().filter_map(Result::ok) {
        let path = entry.path();

        if path.is_file() {
            match path.file_name().and_then(|n| n.to_str()) {
                Some("certificates.csv") => certs.push(path.to_path_buf()),
                Some("recommendations.csv") => recs.push(path.to_path_buf()),
                _ => {}
            }
        }
    }
    info!("Discovered all EPC files");
    (certs, recs)
}

pub fn read_csv_cert_rows(cert_path: PathBuf) -> Result<Vec<EpcCertRow>, csv::Error> {
    let mut cert_csv_reader = csv::ReaderBuilder::new()
        .has_headers(true)
        .from_path(cert_path);

    match cert_csv_reader {
        Ok(mut csv_reader) => {
            let cert_rows: Vec<EpcCertRow> =
                match csv_reader.deserialize().collect::<Result<_, _>>() {
                    Ok(rows) => rows,
                    Err(e) => return Err(e),
                };

            Ok(cert_rows)
        }

        Err(e) => Err(e),
    }
}
