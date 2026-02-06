use chrono::{DateTime, Utc};
use once_cell::sync::Lazy;
use regex::Regex;

pub static POSTCODE_REGEX: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"^(?:(?P<a1>[Gg][Ii][Rr])(?P<d1>) (?P<s1>0)(?P<u1>[Aa]{2}))|(?:(?:(?:(?P<a2>[A-Za-z])(?P<d2>[0-9]{1,2}))|(?:(?:(?P<a3>[A-Za-z][A-Ha-hJ-Yj-y])(?P<d3>[0-9]{1,2}))|(?:(?:(?P<a4>[A-Za-z])(?P<d4>[0-9][A-Za-z]))|(?:(?P<a5>[A-Za-z][A-Ha-hJ-Yj-y])(?P<d5>[0-9]?[A-Za-z]))))) (?P<s2>[0-9])(?P<u2>[A-Za-z]{2}))$"
    ).expect("postcode regex must compile")
});


#[derive(Debug, Clone)]
pub struct PostcodeRow {
    pub postcode: String,
    pub street: String,
    pub town: String,
    pub district: String,
    pub county: String,
    pub outcode: String,
    pub area: String,
    pub sector: String
}

#[derive(Debug, Clone)]
pub struct HouseRow {
    pub houseid: String,
    pub paon: String,
    pub saon: String,
    pub postcode: String,
    pub property_type: String,
}

#[derive(Debug, Clone)]
pub struct SaleRow {
    pub tui: String,
    pub price: i64,
    pub date: DateTime<Utc>,
    pub new_build: bool,
    pub freehold: bool,
    pub ppd_cat: String,
    pub houseid: String,
}

#[derive(Debug)]
pub enum RowType {
    ADDITION,
    CHANGE,
    DELETE
}