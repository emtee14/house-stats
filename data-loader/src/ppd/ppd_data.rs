use chrono::{DateTime, NaiveDateTime, Utc};
use log::info;
use regex::{Captures};
use sha2::{Digest, Sha256};
use serde::Deserialize;
use super::common::{HouseRow, PostcodeRow, RowType, SaleRow, POSTCODE_REGEX};

const MONTHLY_FILE: &str = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update.txt";
const MONO_FILE: &str = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.txt";

#[derive(Deserialize)]
pub struct PpdCsvRow {
    tui: String,
    price: i64,
    date: String,
    postcode: String,
    property_type: String,
    new_build: String,
    duration: String,
    paon: String,
    saon: String,
    street: String,
    _locality: String,
    town: String,
    district: String,
    county: String,
    ppd_cat: String,
    record_status: String,
}


async fn download_monthly_ppd() -> Result<String, reqwest::Error> {
    info!("Downloading monthly ppd data");
    let resp = match reqwest::get(MONTHLY_FILE).await {
        Ok(resp) => resp,
        Err(e) => return Err(e),
    };
    let body = match resp.text().await {
        Ok(body) => body,
        Err(e) => return Err(e),
    };
    info!("Monthly ppd download successful");

    Ok(body)
}

pub async fn download_all_ppd() -> Result<String, reqwest::Error> {
    info!("Downloading all ppd data");
    let resp = match reqwest::get(MONO_FILE).await {
        Ok(resp) => resp,
        Err(e) => return Err(e),
    };
    let body = match resp.text().await {
        Ok(body) => body,
        Err(e) => return Err(e),
    };
    info!("All ppd download successful");

    Ok(body)
}

pub async fn check_for_update(previous_hash: crypto_common::Output<Sha256>) -> Result<String, reqwest::Error> {
    let mut monthly_file = download_monthly_ppd().await?;

    let new_hash = Sha256::digest(&mut monthly_file);
    println!("Last hash {}", hex::encode(previous_hash.as_slice()));
    println!("New hash {}", hex::encode(new_hash.as_slice()));

    if previous_hash != new_hash {
        Ok(monthly_file)
    } else {
        Ok(String::new())
    }

}

fn normalise_record(record: PpdCsvRow) -> Result<(PostcodeRow, HouseRow, SaleRow, RowType), String> {
    let caps = POSTCODE_REGEX
        .captures(&*record.postcode)
        .ok_or_else(|| "Postcode regex failed, invalid postcode".to_string())?;
    let postcode = record.postcode.clone();


    fn first<'a>(caps: &'a Captures, names: &[&str]) -> &'a str {
        for &name in names {
            if let Some(m) = caps.name(name) {
                return m.as_str();
            }
        }
        ""
    }

    let area = first(&caps, &["a1", "a2", "a3", "a4", "a5"]);
    let district = first(&caps, &["d1", "d2", "d3", "d4", "d5"]);
    let sector_digit = first(&caps, &["s1", "s2"]);

    // Build derived components
    let outcode = format!("{}{}", area, district);
    let sector = format!("{}{} {}", area, district, sector_digit);


    let postcode_row = PostcodeRow {
        postcode: postcode.clone(),
        street: record.street,
        town: record.town,
        district: record.district,
        county: record.county,
        outcode: outcode,
        area: area.to_string(),
        sector: sector
    };

    let mut house_id = String::new();
    house_id.push_str(&record.paon);
    house_id.push_str(&record.saon);
    house_id.push_str(postcode_row.postcode.as_str());

    let house_row = HouseRow {
        houseid: house_id.clone(),
        paon: record.paon,
        saon: record.saon,
        postcode: postcode,
        property_type: record.property_type,
    };

    let sale_date = NaiveDateTime::parse_from_str(&*record.date, "%Y-%m-%d %H:%M")
        .expect("invalid datetime format");

    let sale_row = SaleRow {
        tui: record.tui[1..record.tui.len() - 1].to_string(),
        price: record.price,
        date: DateTime::from_utc(sale_date, Utc),
        new_build: if record.new_build  == "N" { true} else {false},
        freehold: if record.duration  == "F" { true} else {false},
        ppd_cat: record.ppd_cat,
        houseid: house_id,
    };
    let row_type = if record.record_status == "A" {RowType::ADDITION} else if record.record_status == "C" {RowType::CHANGE} else {RowType::DELETE};

    Ok((postcode_row, house_row, sale_row, row_type))
}

pub fn normalise_record_list(rows: Vec<PpdCsvRow>) -> (Vec<(PostcodeRow, HouseRow, SaleRow)>, Vec<(PostcodeRow, HouseRow, SaleRow)>) {
    let mut additions: Vec<(PostcodeRow, HouseRow, SaleRow)> = Vec::new();
    let mut deletions: Vec<(PostcodeRow, HouseRow, SaleRow)> = Vec::new();

    for sale in rows {
        let (postcode, house, sale, row_type) = match normalise_record(sale) {
            Ok(row) => row,
            Err(_) => continue,
        };

        match row_type {
            RowType::ADDITION | RowType::CHANGE => {
                additions.push((postcode, house, sale));
            }
            RowType::DELETE => {
                deletions.push((postcode, house, sale));
            }
        }
    }

    (additions, deletions)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ppd_row_postcoe(postcode: &str) -> PpdCsvRow {
        PpdCsvRow {
            tui: "{hello-tui}".to_string(),
            price: 0,
            date: "2021-11-15 00:00".to_string(),
            postcode: postcode.to_string(),
            property_type: "".to_string(),
            new_build: "".to_string(),
            duration: "".to_string(),
            paon: "".to_string(),
            saon: "".to_string(),
            street: "".to_string(),
            _locality: "".to_string(),
            town: "".to_string(),
            district: "".to_string(),
            county: "".to_string(),
            ppd_cat: "".to_string(),
            record_status: "".to_string(),
        }
    }

    #[test]
    fn normalises_valid_postcode() {
        let record = ppd_row_postcoe("LS17 3AD");

        let row = normalise_record(record).expect("should parse postcode");

        assert_eq!(row.0.area, "LS");
        assert_eq!(row.0.outcode, "LS17");
        assert_eq!(row.0.sector, "LS17 3");
    }

    #[test]
    fn normalises_short_district_postcode() {
        let record = ppd_row_postcoe("SW1A 1AA");

        let row = normalise_record(record).unwrap();

        assert_eq!(row.0.area, "SW");
        assert_eq!(row.0.outcode, "SW1A");
        assert_eq!(row.0.sector, "SW1A 1");
    }

    #[test]
    fn rejects_invalid_postcode() {
        let record = ppd_row_postcoe("NOT A POSTCODE");

        let err = normalise_record(record).unwrap_err();

        assert!(err.contains("invalid postcode"));
    }
}