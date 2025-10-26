#!/usr/bin/env python3

import datetime
import importlib.util
import sys

import pandas
import pandas as pd

import helpers.irradiance_transpositions
import helpers.output_estimator
import helpers.reflection_estimator
import plotter
from config import Config
from helpers import panel_temperature_estimator, solar_irradiance_estimator

"""
Main file, contains examples on how to call the functions from other files.

Modify parameters in file config.py in order to change the simulated installation location and other installation
parameters.

full_processing_of_fmi_open_data()
-generates solar pv forecast data with fmi open and plots a minimal plot

full_processing_of_pvlib_open_data()
-generates solar pv forecast data with pvlib and plots a minimal plot

get_fmi_data(day_range)
-generates a power generation dataframe by using fmi open

get_pvlib_data(day_range)
-generates a power generation dataframe by using pvlib

combined_processing_of_data()
-used get_fmi_data and get_pvlib_data to generate dataframes. Plots the data with plotter monoplot.
plot shows power(W) and energy(kWh) values for each day.

Author: TimoSalola (Timo Salola).
"""


def print_full(x: pandas.DataFrame):
    """
    Prints a dataframe without leaving any columns or rows out. Useful for debugging.
    """

    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1400)
    pd.set_option("display.float_format", "{:10,.2f}".format)
    pd.set_option("display.max_colwidth", None)
    print(x)
    pd.reset_option("display.max_rows")
    pd.reset_option("display.max_columns")
    pd.reset_option("display.width")
    pd.reset_option("display.float_format")
    pd.reset_option("display.max_colwidth")


def full_processing_of_fmi_open_data(config: Config):
    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(config, date_start, day_count=3, model="fmiopen")

    # step 2. project irradiance components to plane of array:
    data = helpers.irradiance_transpositions.irradiance_df_to_poa_df(config, data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(config, data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data, config.tilt)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data, config.module_elevation)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(config, data)

    # printing and plotting data
    print_full(data)

    plotter.init_plot()
    plotter.add_label_x("Time")
    plotter.add_label_y("Output(W)")
    plotter.add_title("Simulated solar PV system output")
    plotter.plot_curve(data["time"], data["output"], label="Output(W)")
    plotter.plot_kwh_labels(data, config.data_resolution)
    plotter.show_legend()
    plotter.show_plot()


def full_processing_of_pvlib_data(config: Config):
    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(config, date_start, day_count=3, model="pvlib")

    # step 2. project irradiance components to plane of array:
    data = helpers.irradiance_transpositions.irradiance_df_to_poa_df(config, data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(config, data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data, config.tilt)

    # step 4.1. add dummy wind and air temp data
    data = helpers.panel_temperature_estimator.add_dummy_wind_and_temp(data, config.wind_speed, config.air_temp)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data, config.module_elevation)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(config, data)

    # printing and plotting data
    print_full(data)

    plotter.init_plot()
    plotter.add_label_x("Time")
    plotter.add_label_y("Output(W)")
    plotter.add_title("Simulated solar PV system output")
    plotter.plot_curve(data["time"], data["output"], label="Output(W)")
    plotter.plot_kwh_labels(data, config.data_resolution)
    plotter.show_legend()
    plotter.show_plot()


def get_fmi_data(config: Config, day_range=3):
    """
    This function shows the steps used for generating power output data with fmi open. Also returns the power output.
    Note that FMI open only gives irradiance estimates for the next ~64 hours.
    :param day_range: Day count, 1 returns only this day, 3 returns this day and the 2 following days.
    :return: Power output dataframe
    """

    # using a temporary override of data resolution as fmi open operates on 60 minute data sections.
    # saving original data resolution
    original_data_resolution = config.data_resolution
    # setting temporary value for fmi data processing(this is restored back to original value later)
    config.data_resolution = 60

    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    # step 1. simulate irradiance components dni, dhi, ghi:
    data = solar_irradiance_estimator.get_solar_irradiance(config, date_start, day_count=day_range, model="fmiopen")

    # step 2. project irradiance components to plane of array:
    data = helpers.irradiance_transpositions.irradiance_df_to_poa_df(config, data)

    # step 3. simulate how much of irradiance components is absorbed:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(config, data)

    # step 4. compute sum of reflection-corrected components:
    data = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data, config.tilt)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data, config.module_elevation)

    # step 6. estimate power output
    data = helpers.output_estimator.add_output_to_df(config, data)

    config.data_resolution = original_data_resolution

    return data


def get_pvlib_data(config: Config, day_range=3, data_fmi=None):
    """
    This function shows the steps used for generating power output data with pvlib. Also returns the power output.
    PVlib is fully simulated, no restrictions on day range.
    :param day_range: Day count, 1 returns only this day, 3 returns this day and the 2 following days.
    :param data_fmi: If fmi df is given here, it will be used as weather data donor df
    :return: Power output dataframe
    """
    # date for simulation:
    today = datetime.date.today()
    date_start = datetime.datetime(today.year, today.month, today.day)

    data_pvlib = solar_irradiance_estimator.get_solar_irradiance(config, date_start, day_count=day_range, model="pvlib")

    # step 2. project irradiance components to plane of array:
    data_pvlib = helpers.irradiance_transpositions.irradiance_df_to_poa_df(config, data_pvlib)

    # step 3. simulate how much of irradiance components is absorbed:
    data_pvlib = helpers.reflection_estimator.add_reflection_corrected_poa_components_to_df(config, data_pvlib)

    # step 4. compute sum of reflection-corrected components:
    data_pvlib = helpers.reflection_estimator.add_reflection_corrected_poa_to_df(data_pvlib, config.tilt)

    # step 4.1. adding wind and air speed to dataframe
    if data_fmi is not None:
        # getting data from fmi dataframe if one was given
        data_pvlib = panel_temperature_estimator.add_wind_and_temp_to_df1_from_df2(data_pvlib, data_fmi)
    else:
        # using dummy values if no df was given
        data_pvlib = helpers.panel_temperature_estimator.add_dummy_wind_and_temp(data_pvlib, config.wind_speed, config.air_temp)

    # step 5. estimate panel temperature based on wind speed, air temperature and absorbed radiation
    data_pvlib = helpers.panel_temperature_estimator.add_estimated_panel_temperature(data_pvlib, config.module_elevation)

    # step 6. estimate power output
    data_pvlib = helpers.output_estimator.add_output_to_df(config, data_pvlib)

    data_pvlib = data_pvlib.dropna()

    return data_pvlib


def combined_processing_of_data(config: Config):
    """
    Uses both pvlib and fmi open to compute solar irradiance for the next 4 days and plots both
    :return:
    """

    day_range = 3

    print("Simulating clear sky and weather model based PV generation for the next " + str(day_range) + " days.")
    # fetching fmi data and generating solar pv output df

    data_fmi = get_fmi_data(config, day_range)

    # generating pvlib irradiance values and clear sky pv dataframe, passing fmi data to pvlib generator functions
    # for wind and air temp transfer
    data_pvlib = get_pvlib_data(config, day_range, data_fmi)

    # this line prints the full results into console/terminal

    if config.console_print:
        print("-------------------------------------------------------------------------------------------------------")
        print("Output table printing is turned on in the config.py file")
        print("-----Data-----")

        print_full(data_fmi)

        print("-----Columns explained-----")
        print("[index(Time)]: Meteorological time. In meteorology, timestamp for 13:00 represents the time 12:00-13:00.")
        print("[time]: This is time index shifted by 30min. More useful than the meteorological time for physics.")
        print(
            "[dni, dhi, ghi]: Irradiance types, these can be used for estimating radiation from direct radiation,"
            " atmosphere scattered radiation and ground reflected radiation."
        )
        print("[albedo]: Ground reflectivity near installation. This is retrieved from fmi open data service. Should bebetween 0 and 1.")
        print("[T]: Air temperature at 2m.")
        print("[wind]: Wind speed at 2m.")
        print("[cloud_cover]: Cloudiness percentage, between 0 and 100.")
        print(
            "[dni_poa, dhi_poa, ghi_poa]: Transpositions of dni, dhi and ghi to the plane of array(POA). These values"
            " are always positive and lower than their non _poa counterparts."
        )
        print(
            "[poa]: Sum of dni_poa, dhi_poa, ghi_poa. Represents the amount of radiation reaching the panel surface."
            " This does not account for panel reflectivity."
        )
        print(
            "[dni_rc, dhi_rc, ghi_rc]: Transpositions of radiation types with reflection corrections. These are lower"
            "than their '_poa' counterparts."
        )
        print("[poa_ref_cor]: Sum of dni_rc, dhi_rc and ghi_rc. This represents the amount of radiation absorbed by the solar panels.")
        print("[module_temp]: Estimated value for solar panel temperature. Based on air temp, wind speed and radiation.")
        print("[output]: System output in watts.")
        print("Note that all values before [output] are for a simulated theoretical 1m² panel.")
        print("-------------------------------------------------------------------------------------------------------")

    # this line saves the results as a csv file
    if config.save_csv:
        print("-------------------------------------------------------------------------------------------------------")
        print("Output table csv exporting is turned on in the config.py file")
        filename = config.save_directory + config.site_name + "-" + str(datetime.date.today()) + ".csv"
        data_fmi.to_csv(filename, float_format="%.2f")
        print("Saved csv as: " + filename)
        print("-------------------------------------------------------------------------------------------------------")

    # Save result in json format
    if config.save_json:
        print("-------------------------------------------------------------------------------------------------------")
        print("json exporting turned on in the config.py file")
        filename = config.save_directory + config.site_name + "-" + str(datetime.date.today()) + "-forecasted_production.json"
        data_fmi.to_json(filename, orient="records", date_format="iso", indent=4)
        print("Saved weather model based production forecast json as: " + filename)

        filename = config.save_directory + config.site_name + "-" + str(datetime.date.today()) + "-theoretical_production.json"
        data_pvlib.to_json(filename, orient="records", date_format="iso", indent=4)
        print("Saved theoretical blue sky generation json as: " + filename)
        print("-------------------------------------------------------------------------------------------------------")

    # plotting both fmi and pvlib data
    if config.save_plot:
        print("-------------------------------------------------------------------------------------------------------")
        print("Plots exporting turned on in the config.py file")
        plotter.plot_fmi_pvlib_mono(config, data_fmi, data_pvlib)


def load_config_from_file(config_file: str) -> Config:
    """
    Loads a Config class from a given file path.
    :param config_file_path: Path to the config file.
    :return: Config object.
    """
    # Import the config file dynamically

    # Import the Config class from the specified config file.
    # And initialize it as config.
    spec = importlib.util.spec_from_file_location("config_module", config_file)
    if spec is None or spec.loader is None:
        print(f"Cannot import module from {config_file}")
        sys.exit(1)

    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    return config_module.Config()


if __name__ == "__main__":
    # Check if a config file was provided as command line argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        print(f"Loading config file {config_file}")
        config = load_config_from_file(config_file)
    else:
        print("Using default config file config.py")
        config = Config()

    # if executed as main file, run combined processing as our "main" function
    combined_processing_of_data(config)
