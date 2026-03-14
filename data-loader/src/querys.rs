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

pub const CREATE_EPC_CERT_TABLE: &str = "
CREATE TABLE epc_certificates (
    lmk_key VARCHAR(64) PRIMARY KEY,

    address1 VARCHAR(150),
    address2 VARCHAR(104),
    address3 VARCHAR(100),
    address TEXT,
    postcode VARCHAR(8),
    post_town VARCHAR(50),

    building_reference_number VARCHAR(12),

    current_energy_rating VARCHAR(8),
    potential_energy_rating VARCHAR(8),
    current_energy_efficiency INTEGER,
    potential_energy_efficiency INTEGER,

    property_type VARCHAR(76),
    built_form VARCHAR(20),

    inspection_date DATE,
    lodgement_date DATE,
    lodgement_datetime TIMESTAMP,

    local_authority VARCHAR(9),
    local_authority_name TEXT,
    constituency VARCHAR(9),
    constituency_name TEXT,
    county VARCHAR(24),

    transaction_type VARCHAR(82),

    environment_impact_current INTEGER,
    environment_impact_potential INTEGER,

    energy_consumption_current NUMERIC(10,2),
    energy_consumption_potential NUMERIC(10,2),

    co2_emissions_current NUMERIC(10,3),
    co2_emiss_curr_per_floor_area NUMERIC(10,3),
    co2_emissions_potential NUMERIC(10,3),

    lighting_cost_current NUMERIC(12,2),
    lighting_cost_potential NUMERIC(12,2),
    heating_cost_current NUMERIC(12,2),
    heating_cost_potential NUMERIC(12,2),
    hot_water_cost_current NUMERIC(12,2),
    hot_water_cost_potential NUMERIC(12,2),

    total_floor_area NUMERIC(10,2),

    energy_tariff VARCHAR(16),
    mains_gas_flag VARCHAR(1),

    floor_level VARCHAR(13),
    flat_top_storey VARCHAR(1),
    flat_storey_count INTEGER,

    main_heating_controls VARCHAR(19),
    multi_glaze_proportion NUMERIC(5,2),
    glazed_type VARCHAR(45),
    glazed_area VARCHAR(22),

    extension_count NUMERIC(4,1),
    number_habitable_rooms NUMERIC(5,1),
    number_heated_rooms NUMERIC(5,1),

    low_energy_lighting INTEGER,
    number_open_fireplaces INTEGER,

    hotwater_description VARCHAR(95),
    hot_water_energy_eff VARCHAR(9),
    hot_water_env_eff VARCHAR(9),

    floor_description VARCHAR(120),
    floor_energy_eff VARCHAR(9),
    floor_env_eff VARCHAR(9),

    windows_description VARCHAR(54),
    windows_energy_eff VARCHAR(9),
    windows_env_eff VARCHAR(9),

    walls_description VARCHAR(121),
    walls_energy_eff VARCHAR(9),
    walls_env_eff VARCHAR(9),

    secondheat_description VARCHAR(97),
    sheating_energy_eff VARCHAR(9),
    sheating_env_eff VARCHAR(9),

    roof_description VARCHAR(92),
    roof_energy_eff VARCHAR(9),
    roof_env_eff VARCHAR(9),

    mainheat_description VARCHAR(140),
    mainheat_energy_eff VARCHAR(9),
    mainheat_env_eff VARCHAR(9),

    mainheatcont_description VARCHAR(110),
    mainheatc_energy_eff VARCHAR(9),
    mainheatc_env_eff VARCHAR(9),

    lighting_description VARCHAR(120),
    lighting_energy_eff VARCHAR(9),
    lighting_env_eff VARCHAR(9),

    main_fuel VARCHAR(93),

    wind_turbine_count NUMERIC(4,1),

    heat_loss_corridor VARCHAR(17),
    unheated_corridor_length NUMERIC(10,2),

    floor_height NUMERIC(6,2),
    photo_supply NUMERIC(5,2),
    solar_water_heating_flag VARCHAR(1),
    mechanical_ventilation VARCHAR(50),

    construction_age_band VARCHAR(31),
    tenure VARCHAR(150),

    fixed_lighting_outlets_count NUMERIC(6,1),
    low_energy_fixed_light_count NUMERIC(6,1),

    uprn BIGINT,
    uprn_source VARCHAR(15),

    report_type INTEGER
);
CREATE INDEX epc_postcode_idx ON epc_certificates(postcode);
CREATE INDEX epc_uprn_idx ON epc_certificates(uprn);
CREATE INDEX epc_local_authority_idx ON epc_certificates(local_authority);
CREATE INDEX epc_rating_idx ON epc_certificates(current_energy_rating);
CREATE INDEX epc_floor_area_idx ON epc_certificates(total_floor_area);
CREATE INDEX epc_lodgement_date_idx ON epc_certificates(lodgement_date);
";
