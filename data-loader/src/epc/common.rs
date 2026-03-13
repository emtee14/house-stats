use chrono::{DateTime, NaiveDate, NaiveDateTime, Utc};
use serde::{self, Deserialize, Deserializer};
use std::time::SystemTime;

fn empty_string_none<'de, D>(d: D) -> Result<Option<String>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.filter(|v| !v.trim().is_empty()))
}

fn opt_i32<'de, D>(d: D) -> Result<Option<i32>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| v.trim().parse().ok()))
}

fn opt_i64<'de, D>(d: D) -> Result<Option<i64>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| v.trim().parse().ok()))
}

fn opt_f32<'de, D>(d: D) -> Result<Option<f32>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| v.trim().parse().ok()))
}

fn opt_bool_yn<'de, D>(d: D) -> Result<Option<bool>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(match s.as_deref() {
        Some("Y") => Some(true),
        Some("N") => Some(false),
        _ => None,
    })
}

fn opt_rating<'de, D>(d: D) -> Result<Option<String>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| {
        let t = v.trim().to_uppercase();
        match t.as_str() {
            "A" | "B" | "C" | "D" | "E" | "F" | "G" => Some(t),
            _ => None,
        }
    }))
}

fn opt_date<'de, D>(d: D) -> Result<Option<SystemTime>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| {
        NaiveDate::parse_from_str(&v, "%Y-%m-%d")
            .ok()
            .and_then(|d| d.and_hms_opt(0, 0, 0))
            .map(|dt| DateTime::<Utc>::from_naive_utc_and_offset(dt, Utc))
            .map(|dt| SystemTime::from(dt))
    }))
}

fn opt_datetime<'de, D>(d: D) -> Result<Option<SystemTime>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(d)?;
    Ok(s.and_then(|v| {
        NaiveDateTime::parse_from_str(&v, "%Y-%m-%d %H:%M:%S")
            .ok()
            .map(|dt| DateTime::<Utc>::from_naive_utc_and_offset(dt, Utc))
            .map(|dt| SystemTime::from(dt))
    }))
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub struct EpcCertRow {
    pub lmk_key: String,

    #[serde(deserialize_with = "empty_string_none")]
    pub address1: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub address2: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub address3: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub postcode: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub building_reference_number: Option<String>,

    #[serde(deserialize_with = "opt_rating")]
    pub current_energy_rating: Option<String>,
    #[serde(deserialize_with = "opt_rating")]
    pub potential_energy_rating: Option<String>,

    #[serde(deserialize_with = "opt_i32")]
    pub current_energy_efficiency: Option<i32>,
    #[serde(deserialize_with = "opt_i32")]
    pub potential_energy_efficiency: Option<i32>,

    #[serde(deserialize_with = "empty_string_none")]
    pub property_type: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub built_form: Option<String>,

    #[serde(deserialize_with = "opt_date")]
    pub inspection_date: Option<SystemTime>,

    #[serde(deserialize_with = "empty_string_none")]
    pub local_authority: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub constituency: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub county: Option<String>,

    #[serde(deserialize_with = "opt_date")]
    pub lodgement_date: Option<SystemTime>,

    #[serde(deserialize_with = "empty_string_none")]
    pub transaction_type: Option<String>,

    #[serde(deserialize_with = "opt_i32")]
    pub environment_impact_current: Option<i32>,
    #[serde(deserialize_with = "opt_i32")]
    pub environment_impact_potential: Option<i32>,

    #[serde(deserialize_with = "opt_f32")]
    pub energy_consumption_current: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub energy_consumption_potential: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub co2_emissions_current: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub co2_emiss_curr_per_floor_area: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub co2_emissions_potential: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub lighting_cost_current: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub lighting_cost_potential: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub heating_cost_current: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub heating_cost_potential: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub hot_water_cost_current: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub hot_water_cost_potential: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub total_floor_area: Option<f32>,

    #[serde(deserialize_with = "empty_string_none")]
    pub energy_tariff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mains_gas_flag: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub floor_level: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub flat_top_storey: Option<String>,
    #[serde(deserialize_with = "opt_i32")]
    pub flat_storey_count: Option<i32>,

    #[serde(deserialize_with = "empty_string_none")]
    pub main_heating_controls: Option<String>,

    #[serde(deserialize_with = "opt_f32")]
    pub multi_glaze_proportion: Option<f32>,
    #[serde(deserialize_with = "empty_string_none")]
    pub glazed_type: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub glazed_area: Option<String>,

    #[serde(deserialize_with = "opt_f32")]
    pub extension_count: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub number_habitable_rooms: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub number_heated_rooms: Option<f32>,

    #[serde(deserialize_with = "opt_i32")]
    pub low_energy_lighting: Option<i32>,
    #[serde(deserialize_with = "opt_i32")]
    pub number_open_fireplaces: Option<i32>,

    #[serde(deserialize_with = "empty_string_none")]
    pub hotwater_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub hot_water_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub hot_water_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub floor_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub floor_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub floor_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub windows_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub windows_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub windows_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub walls_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub walls_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub walls_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub secondheat_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub sheating_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub sheating_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub roof_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub roof_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub roof_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub mainheat_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mainheat_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mainheat_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub mainheatcont_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mainheatc_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mainheatc_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub lighting_description: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub lighting_energy_eff: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub lighting_env_eff: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub main_fuel: Option<String>,

    #[serde(deserialize_with = "opt_f32")]
    pub wind_turbine_count: Option<f32>,

    #[serde(deserialize_with = "empty_string_none")]
    pub heat_loss_corridor: Option<String>,
    #[serde(deserialize_with = "opt_f32")]
    pub unheated_corridor_length: Option<f32>,

    #[serde(deserialize_with = "opt_f32")]
    pub floor_height: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub photo_supply: Option<f32>,
    #[serde(deserialize_with = "empty_string_none")]
    pub solar_water_heating_flag: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub mechanical_ventilation: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub address: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub local_authority_label: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub constituency_label: Option<String>,
    #[serde(deserialize_with = "empty_string_none")]
    pub posttown: Option<String>,

    #[serde(deserialize_with = "empty_string_none")]
    pub construction_age_band: Option<String>,
    #[serde(deserialize_with = "opt_date")]
    pub lodgement_datetime: Option<SystemTime>,
    #[serde(deserialize_with = "empty_string_none")]
    pub tenure: Option<String>,

    #[serde(deserialize_with = "opt_f32")]
    pub fixed_lighting_outlets_count: Option<f32>,
    #[serde(deserialize_with = "opt_f32")]
    pub low_energy_fixed_light_count: Option<f32>,

    #[serde(deserialize_with = "opt_i64")]
    pub uprn: Option<i64>,
    #[serde(deserialize_with = "empty_string_none")]
    pub uprn_source: Option<String>,

    #[serde(deserialize_with = "opt_i32")]
    pub report_type: Option<i32>,
}

// LMK_KEY
// ADDRESS1
// ADDRESS2
// ADDRESS3
// POSTCODE
// BUILDING_REFERENCE_NUMBER
// CURRENT_ENERGY_RATING
// POTENTIAL_ENERGY_RATING
// CURRENT_ENERGY_EFFICIENCY
// POTENTIAL_ENERGY_EFFICIENCY
// PROPERTY_TYPE
// BUILT_FORM
// INSPECTION_DATE
// LOCAL_AUTHORITY
// CONSTITUENCY
// COUNTY
// LODGEMENT_DATE
// TRANSACTION_TYPE
// ENVIRONMENT_IMPACT_CURRENT
// ENVIRONMENT_IMPACT_POTENTIAL
// ENERGY_CONSUMPTION_CURRENT
// ENERGY_CONSUMPTION_POTENTIAL
// CO2_EMISSIONS_CURRENT
// CO2_EMISS_CURR_PER_FLOOR_AREA
// CO2_EMISSIONS_POTENTIAL
// LIGHTING_COST_CURRENT
// LIGHTING_COST_POTENTIAL
// HEATING_COST_CURRENT
// HEATING_COST_POTENTIAL
// HOT_WATER_COST_CURRENT
// HOT_WATER_COST_POTENTIAL
// TOTAL_FLOOR_AREA
// ENERGY_TARIFF
// MAINS_GAS_FLAG
// FLOOR_LEVEL
// FLAT_TOP_STOREY
// FLAT_STOREY_COUNT
// MAIN_HEATING_CONTROLS
// MULTI_GLAZE_PROPORTION
// GLAZED_TYPE
// GLAZED_AREA
// EXTENSION_COUNT
// NUMBER_HABITABLE_ROOMS
// NUMBER_HEATED_ROOMS
// LOW_ENERGY_LIGHTING
// NUMBER_OPEN_FIREPLACES
// HOTWATER_DESCRIPTION
// HOT_WATER_ENERGY_EFF
// HOT_WATER_ENV_EFF
// FLOOR_DESCRIPTION
// FLOOR_ENERGY_EFF
// FLOOR_ENV_EFF
// WINDOWS_DESCRIPTION
// WINDOWS_ENERGY_EFF
// WINDOWS_ENV_EFF
// WALLS_DESCRIPTION
// WALLS_ENERGY_EFF
// WALLS_ENV_EFF
// SECONDHEAT_DESCRIPTION
// SHEATING_ENERGY_EFF
// SHEATING_ENV_EFF
// ROOF_DESCRIPTION
// ROOF_ENERGY_EFF
// ROOF_ENV_EFF
// MAINHEAT_DESCRIPTION
// MAINHEAT_ENERGY_EFF
// MAINHEAT_ENV_EFF
// MAINHEATCONT_DESCRIPTION
// MAINHEATC_ENERGY_EFF
// MAINHEATC_ENV_EFF
// LIGHTING_DESCRIPTION
// LIGHTING_ENERGY_EFF
// LIGHTING_ENV_EFF
// MAIN_FUEL
// WIND_TURBINE_COUNT
// HEAT_LOSS_CORRIDOR
// UNHEATED_CORRIDOR_LENGTH
// FLOOR_HEIGHT
// PHOTO_SUPPLY
// SOLAR_WATER_HEATING_FLAG
// MECHANICAL_VENTILATION
// ADDRESS
// LOCAL_AUTHORITY_LABEL
// CONSTITUENCY_LABEL
// POSTTOWN
// CONSTRUCTION_AGE_BAND
// LODGEMENT_DATETIME
// TENURE
// FIXED_LIGHTING_OUTLETS_COUNT
// LOW_ENERGY_FIXED_LIGHT_COUNT
// UPRN
// UPRN_SOURCE
// REPORT_TYPE
