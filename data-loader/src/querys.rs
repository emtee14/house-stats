pub const CREATE_CONFIG_TABLE_QUERY: &str = "
CREATE TABLE IF NOT EXISTS config (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE,

    last_ppd_update   TIMESTAMPTZ NOT NULL,
    last_ppd_file     BYTEA NOT NULL,
    last_epc_update   TIMESTAMPTZ NOT NULL,
    last_epc_file     BYTEA NOT NULL,
    last_linking_run  TIMESTAMPTZ NOT NULL,
    last_init_data    TIMESTAMPTZ NOT NULL

    CONSTRAINT singleton_true CHECK (singleton)
);
";


pub const CREATE_POSTCODE_TABLE_QUERY: &str = "CREATE TABLE IF NOT EXISTS postcodes (
    postcode varchar(15) not null constraint postcode_key primary key,
    street varchar(70) ,
    town varchar(50) ,
    district varchar(50) ,
    county varchar(50) ,
    outcode varchar(4) ,
    area varchar(2) ,
    sector varchar(6)
    );
create unique index postcode_idx on postcodes (postcode) ;
create index area_idx on postcodes (area);
create index county_idx on postcodes (county);
create index district_idx on postcodes (district);
create index outcode_idx on postcodes (outcode);
create index sector_idx on postcodes (sector);
create index street_idx on postcodes (street);
create index town_idx on postcodes (town);
";

pub const CREATE_HOUSES_TABLE_QUERY: &str = "CREATE TABLE IF NOT EXISTS houses (
    houseid varchar(150) not null constraint houseid primary key,
    paon varchar(150),
    saon varchar(150),
    postcode varchar(15) constraint postcodes_keys references postcodes,
    type char
    );
create index postcodes_idx on houses (postcode);
create index type_idx on houses (type);
";

pub const CREATE_SALE_TABLE_QUERY: &str = "CREATE TABLE IF NOT EXISTS sales (
    tui varchar(36) not null constraint tui_key primary key,
    price integer,
    date TIMESTAMPTZ,
    new boolean,
    freehold boolean,
    ppd_cat char,
    houseid varchar(150) constraint houseid_fk references houses );
create index date_idx on sales (date);
create index freehold_idx on sales (freehold desc);
create index ppd_cat_idx on sales (ppd_cat);";


