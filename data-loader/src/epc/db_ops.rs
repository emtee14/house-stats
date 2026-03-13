use crate::database::HouseStatsDatabase;
use crate::epc::common::EpcCertRow;
use std::time::SystemTime;

pub async fn batch_insert_epc_certs(
    tx: &tokio_postgres::Transaction<'_>,
    rows: &[EpcCertRow],
) -> Result<(), tokio_postgres::Error> {
    if rows.is_empty() {
        return Ok(());
    }
    // ---- Build vectors ----

    let lmk_key: Vec<&str> = rows.iter().map(|r| r.lmk_key.as_str()).collect();

    let address1: Vec<Option<&str>> = rows.iter().map(|r| r.address1.as_deref()).collect();
    let address2: Vec<Option<&str>> = rows.iter().map(|r| r.address2.as_deref()).collect();
    let address3: Vec<Option<&str>> = rows.iter().map(|r| r.address3.as_deref()).collect();
    let postcode: Vec<Option<&str>> = rows.iter().map(|r| r.postcode.as_deref()).collect();

    let building_reference_number: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.building_reference_number.as_deref())
        .collect();

    let current_energy_rating: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.current_energy_rating.as_deref())
        .collect();

    let potential_energy_rating: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.potential_energy_rating.as_deref())
        .collect();

    let current_energy_efficiency: Vec<Option<i32>> =
        rows.iter().map(|r| r.current_energy_efficiency).collect();

    let potential_energy_efficiency: Vec<Option<i32>> =
        rows.iter().map(|r| r.potential_energy_efficiency).collect();

    let property_type: Vec<Option<&str>> =
        rows.iter().map(|r| r.property_type.as_deref()).collect();

    let built_form: Vec<Option<&str>> = rows.iter().map(|r| r.built_form.as_deref()).collect();

    let inspection_date: Vec<Option<SystemTime>> = rows.iter().map(|r| r.inspection_date).collect();

    let local_authority: Vec<Option<&str>> =
        rows.iter().map(|r| r.local_authority.as_deref()).collect();

    let constituency: Vec<Option<&str>> = rows.iter().map(|r| r.constituency.as_deref()).collect();

    let county: Vec<Option<&str>> = rows.iter().map(|r| r.county.as_deref()).collect();

    let lodgement_date: Vec<Option<SystemTime>> = rows.iter().map(|r| r.lodgement_date).collect();

    let transaction_type: Vec<Option<&str>> =
        rows.iter().map(|r| r.transaction_type.as_deref()).collect();

    let environment_impact_current: Vec<Option<i32>> =
        rows.iter().map(|r| r.environment_impact_current).collect();

    let environment_impact_potential: Vec<Option<i32>> = rows
        .iter()
        .map(|r| r.environment_impact_potential)
        .collect();

    let energy_consumption_current: Vec<Option<f32>> =
        rows.iter().map(|r| r.energy_consumption_current).collect();

    let energy_consumption_potential: Vec<Option<f32>> = rows
        .iter()
        .map(|r| r.energy_consumption_potential)
        .collect();

    let co2_emissions_current: Vec<Option<f32>> =
        rows.iter().map(|r| r.co2_emissions_current).collect();

    let co2_emiss_curr_per_floor_area: Vec<Option<f32>> = rows
        .iter()
        .map(|r| r.co2_emiss_curr_per_floor_area)
        .collect();

    let co2_emissions_potential: Vec<Option<f32>> =
        rows.iter().map(|r| r.co2_emissions_potential).collect();

    let lighting_cost_current: Vec<Option<f32>> =
        rows.iter().map(|r| r.lighting_cost_current).collect();

    let lighting_cost_potential: Vec<Option<f32>> =
        rows.iter().map(|r| r.lighting_cost_potential).collect();

    let heating_cost_current: Vec<Option<f32>> =
        rows.iter().map(|r| r.heating_cost_current).collect();

    let heating_cost_potential: Vec<Option<f32>> =
        rows.iter().map(|r| r.heating_cost_potential).collect();

    let hot_water_cost_current: Vec<Option<f32>> =
        rows.iter().map(|r| r.hot_water_cost_current).collect();

    let hot_water_cost_potential: Vec<Option<f32>> =
        rows.iter().map(|r| r.hot_water_cost_potential).collect();

    let total_floor_area: Vec<Option<f32>> = rows.iter().map(|r| r.total_floor_area).collect();

    let energy_tariff: Vec<Option<&str>> =
        rows.iter().map(|r| r.energy_tariff.as_deref()).collect();

    let mains_gas_flag: Vec<Option<&str>> =
        rows.iter().map(|r| r.mains_gas_flag.as_deref()).collect();

    let floor_level: Vec<Option<&str>> = rows.iter().map(|r| r.floor_level.as_deref()).collect();

    let flat_top_storey: Vec<Option<&str>> =
        rows.iter().map(|r| r.flat_top_storey.as_deref()).collect();

    let flat_storey_count: Vec<Option<i32>> = rows.iter().map(|r| r.flat_storey_count).collect();

    let main_heating_controls: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.main_heating_controls.as_deref())
        .collect();

    let multi_glaze_proportion: Vec<Option<f32>> =
        rows.iter().map(|r| r.multi_glaze_proportion).collect();

    let glazed_type: Vec<Option<&str>> = rows.iter().map(|r| r.glazed_type.as_deref()).collect();

    let glazed_area: Vec<Option<&str>> = rows.iter().map(|r| r.glazed_area.as_deref()).collect();

    let extension_count: Vec<Option<f32>> = rows.iter().map(|r| r.extension_count).collect();

    let number_habitable_rooms: Vec<Option<f32>> =
        rows.iter().map(|r| r.number_habitable_rooms).collect();

    let number_heated_rooms: Vec<Option<f32>> =
        rows.iter().map(|r| r.number_heated_rooms).collect();

    let low_energy_lighting: Vec<Option<i32>> =
        rows.iter().map(|r| r.low_energy_lighting).collect();

    let number_open_fireplaces: Vec<Option<i32>> =
        rows.iter().map(|r| r.number_open_fireplaces).collect();

    let hotwater_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.hotwater_description.as_deref())
        .collect();

    let hot_water_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.hot_water_energy_eff.as_deref())
        .collect();

    let hot_water_env_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.hot_water_env_eff.as_deref())
        .collect();

    let floor_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.floor_description.as_deref())
        .collect();

    let floor_energy_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.floor_energy_eff.as_deref()).collect();

    let floor_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.floor_env_eff.as_deref()).collect();

    let windows_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.windows_description.as_deref())
        .collect();

    let windows_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.windows_energy_eff.as_deref())
        .collect();

    let windows_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.windows_env_eff.as_deref()).collect();

    let walls_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.walls_description.as_deref())
        .collect();

    let walls_energy_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.walls_energy_eff.as_deref()).collect();

    let walls_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.walls_env_eff.as_deref()).collect();

    let secondheat_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.secondheat_description.as_deref())
        .collect();

    let sheating_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.sheating_energy_eff.as_deref())
        .collect();

    let sheating_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.sheating_env_eff.as_deref()).collect();

    let roof_description: Vec<Option<&str>> =
        rows.iter().map(|r| r.roof_description.as_deref()).collect();

    let roof_energy_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.roof_energy_eff.as_deref()).collect();

    let roof_env_eff: Vec<Option<&str>> = rows.iter().map(|r| r.roof_env_eff.as_deref()).collect();

    let mainheat_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mainheat_description.as_deref())
        .collect();

    let mainheat_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mainheat_energy_eff.as_deref())
        .collect();

    let mainheat_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.mainheat_env_eff.as_deref()).collect();

    let mainheatcont_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mainheatcont_description.as_deref())
        .collect();

    let mainheatc_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mainheatc_energy_eff.as_deref())
        .collect();

    let mainheatc_env_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mainheatc_env_eff.as_deref())
        .collect();

    let lighting_description: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.lighting_description.as_deref())
        .collect();

    let lighting_energy_eff: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.lighting_energy_eff.as_deref())
        .collect();

    let lighting_env_eff: Vec<Option<&str>> =
        rows.iter().map(|r| r.lighting_env_eff.as_deref()).collect();

    let main_fuel: Vec<Option<&str>> = rows.iter().map(|r| r.main_fuel.as_deref()).collect();

    let wind_turbine_count: Vec<Option<f32>> = rows.iter().map(|r| r.wind_turbine_count).collect();

    let heat_loss_corridor: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.heat_loss_corridor.as_deref())
        .collect();

    let unheated_corridor_length: Vec<Option<f32>> =
        rows.iter().map(|r| r.unheated_corridor_length).collect();

    let floor_height: Vec<Option<f32>> = rows.iter().map(|r| r.floor_height).collect();

    let photo_supply: Vec<Option<f32>> = rows.iter().map(|r| r.photo_supply).collect();

    let solar_water_heating_flag: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.solar_water_heating_flag.as_deref())
        .collect();

    let mechanical_ventilation: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.mechanical_ventilation.as_deref())
        .collect();

    let address: Vec<Option<&str>> = rows.iter().map(|r| r.address.as_deref()).collect();

    let local_authority_label: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.local_authority_label.as_deref())
        .collect();

    let constituency_label: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.constituency_label.as_deref())
        .collect();

    let posttown: Vec<Option<&str>> = rows.iter().map(|r| r.posttown.as_deref()).collect();

    let construction_age_band: Vec<Option<&str>> = rows
        .iter()
        .map(|r| r.construction_age_band.as_deref())
        .collect();

    let lodgement_datetime: Vec<Option<SystemTime>> =
        rows.iter().map(|r| r.lodgement_datetime).collect();

    let tenure: Vec<Option<&str>> = rows.iter().map(|r| r.tenure.as_deref()).collect();

    let fixed_lighting_outlets_count: Vec<Option<f32>> = rows
        .iter()
        .map(|r| r.fixed_lighting_outlets_count)
        .collect();

    let uprn: Vec<Option<i64>> = rows.iter().map(|r| r.uprn).collect();

    let uprn_source: Vec<Option<&str>> = rows.iter().map(|r| r.uprn_source.as_deref()).collect();

    let report_type: Vec<Option<i32>> = rows.iter().map(|r| r.report_type).collect();

    let low_energy_fixed_light_count: Vec<Option<f32>> = rows
        .iter()
        .map(|r| r.low_energy_fixed_light_count)
        .collect();
    // ---- Execute ----

    tx.execute(
        "
    INSERT INTO epc_certificates (
        lmk_key,
        address1, address2, address3, postcode,
        building_reference_number,
        current_energy_rating, potential_energy_rating,
        current_energy_efficiency, potential_energy_efficiency,
        property_type, built_form,
        inspection_date,
        local_authority, constituency, county,
        lodgement_date,
        transaction_type,
        environment_impact_current, environment_impact_potential,
        energy_consumption_current, energy_consumption_potential,
        co2_emissions_current, co2_emiss_curr_per_floor_area, co2_emissions_potential,
        lighting_cost_current, lighting_cost_potential,
        heating_cost_current, heating_cost_potential,
        hot_water_cost_current, hot_water_cost_potential,
        total_floor_area,
        energy_tariff, mains_gas_flag,
        floor_level, flat_top_storey, flat_storey_count,
        main_heating_controls,
        multi_glaze_proportion, glazed_type, glazed_area,
        extension_count, number_habitable_rooms, number_heated_rooms,
        low_energy_lighting, number_open_fireplaces,
        hotwater_description, hot_water_energy_eff, hot_water_env_eff,
        floor_description, floor_energy_eff, floor_env_eff,
        windows_description, windows_energy_eff, windows_env_eff,
        walls_description, walls_energy_eff, walls_env_eff,
        secondheat_description, sheating_energy_eff, sheating_env_eff,
        roof_description, roof_energy_eff, roof_env_eff,
        mainheat_description, mainheat_energy_eff, mainheat_env_eff,
        mainheatcont_description, mainheatc_energy_eff, mainheatc_env_eff,
        lighting_description, lighting_energy_eff, lighting_env_eff,
        main_fuel,
        wind_turbine_count,
        heat_loss_corridor, unheated_corridor_length,
        floor_height, photo_supply, solar_water_heating_flag, mechanical_ventilation,
        address, local_authority_name, constituency_name, post_town,
        construction_age_band, lodgement_datetime, tenure,
        fixed_lighting_outlets_count, low_energy_fixed_light_count,
        uprn, uprn_source,
        report_type
    )
    SELECT *
    FROM UNNEST(
        $1::text[],
        $2::text[], $3::text[], $4::text[], $5::text[],
        $6::text[],
        $7::text[], $8::text[],
        $9::int[], $10::int[],
        $11::text[], $12::text[],
        $13::timestamptz[],
        $14::text[], $15::text[], $16::text[],
        $17::timestamptz[],
        $18::text[],
        $19::int[], $20::int[],
        $21::real[], $22::real[],
        $23::real[], $24::real[], $25::real[],
        $26::real[], $27::real[],
        $28::real[], $29::real[],
        $30::real[], $31::real[],
        $32::real[],
        $33::text[], $34::text[],
        $35::text[], $36::text[], $37::int[],
        $38::text[],
        $39::real[], $40::text[], $41::text[],
        $42::real[], $43::real[], $44::real[],
        $45::int[], $46::int[],
        $47::text[], $48::text[], $49::text[],
        $50::text[], $51::text[], $52::text[],
        $53::text[], $54::text[], $55::text[],
        $56::text[], $57::text[], $58::text[],
        $59::text[], $60::text[], $61::text[],
        $62::text[], $63::text[], $64::text[],
        $65::text[], $66::text[], $67::text[],
        $68::text[], $69::text[], $70::text[],
        $71::text[], $72::text[], $73::text[],
        $74::text[],
        $75::real[],
        $76::text[], $77::real[],
        $78::real[], $79::real[], $80::text[], $81::text[],
        $82::text[], $83::text[], $84::text[], $85::text[],
        $86::text[], $87::timestamptz[], $88::text[],
        $89::real[], $90::real[],
        $91::bigint[], $92::text[],
        $93::int[]
    )
    ON CONFLICT (lmk_key) DO NOTHING
    ",
        &[
            &lmk_key,
            &address1,
            &address2,
            &address3,
            &postcode,
            &building_reference_number,
            &current_energy_rating,
            &potential_energy_rating,
            &current_energy_efficiency,
            &potential_energy_efficiency,
            &property_type,
            &built_form,
            &inspection_date,
            &local_authority,
            &constituency,
            &county,
            &lodgement_date,
            &transaction_type,
            &environment_impact_current,
            &environment_impact_potential,
            &energy_consumption_current,
            &energy_consumption_potential,
            &co2_emissions_current,
            &co2_emiss_curr_per_floor_area,
            &co2_emissions_potential,
            &lighting_cost_current,
            &lighting_cost_potential,
            &heating_cost_current,
            &heating_cost_potential,
            &hot_water_cost_current,
            &hot_water_cost_potential,
            &total_floor_area,
            &energy_tariff,
            &mains_gas_flag,
            &floor_level,
            &flat_top_storey,
            &flat_storey_count,
            &main_heating_controls,
            &multi_glaze_proportion,
            &glazed_type,
            &glazed_area,
            &extension_count,
            &number_habitable_rooms,
            &number_heated_rooms,
            &low_energy_lighting,
            &number_open_fireplaces,
            &hotwater_description,
            &hot_water_energy_eff,
            &hot_water_env_eff,
            &floor_description,
            &floor_energy_eff,
            &floor_env_eff,
            &windows_description,
            &windows_energy_eff,
            &windows_env_eff,
            &walls_description,
            &walls_energy_eff,
            &walls_env_eff,
            &secondheat_description,
            &sheating_energy_eff,
            &sheating_env_eff,
            &roof_description,
            &roof_energy_eff,
            &roof_env_eff,
            &mainheat_description,
            &mainheat_energy_eff,
            &mainheat_env_eff,
            &mainheatcont_description,
            &mainheatc_energy_eff,
            &mainheatc_env_eff,
            &lighting_description,
            &lighting_energy_eff,
            &lighting_env_eff,
            &main_fuel,
            &wind_turbine_count,
            &heat_loss_corridor,
            &unheated_corridor_length,
            &floor_height,
            &photo_supply,
            &solar_water_heating_flag,
            &mechanical_ventilation,
            &address,
            &local_authority_label,
            &constituency_label,
            &posttown,
            &construction_age_band,
            &lodgement_datetime,
            &tenure,
            &fixed_lighting_outlets_count,
            &low_energy_fixed_light_count,
            &uprn,
            &uprn_source,
            &report_type,
        ],
    )
    .await?;

    Ok(())
}

pub async fn insert_epc_cert(
    database: &mut HouseStatsDatabase,
    cert_rows: &Vec<EpcCertRow>,
) -> Result<(), tokio_postgres::Error> {
    for chunk in cert_rows.chunks(1000) {
        let tx = database.db_client.transaction().await?;

        batch_insert_epc_certs(&tx, chunk).await?;
        tx.commit().await?;
    }

    Ok(())
}
