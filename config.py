"""
Config file, used for storing parameters which are installation specific and fixed. Geolocation, panel angles, timezone
and data resolution belong here. Variables in this file should be expected to stay unmodified during a simulation.

Author: TimoSalola (Timo Salola).
"""


class Config:
    ##### Plotting parameters
    # site name used for plotting and saved file name
    site_name = "output_example"
    save_directory = "output/"
    save_plot = True  # value= [True] or [False] this variable toggles plot saving to png on or off
    save_csv = False  # value= [True] or [False] this variable toggles csv file saving on or off
    save_json = False  # value= [True] or [False] this variable toggles json file saving on or off
    console_print = True  # value= [True] or [False] this variable toggles console printing of the full output table on or off

    #### SIMULATED INSTALLATION PARAMETERS BELOW:
    # coordinates
    latitude = 60.2044
    longitude = 24.9625

    # panel angles
    tilt = 15  # degrees. Panel flat on the roof would have tilt of 0. Wall mounted panels have tilt of 90.
    azimuth = 135  # degrees, north is 0 degrees, east 90. Clockwise rotation

    # rated installation power in kW, PV output at standard testing conditions
    rated_power = 21  # unit kW

    # ground albedo near solar panels, 0.25 is PVlib default. Has to be in range [0,1], typical values [0.1, 0.4]
    # grass is 0.25, snow 0.8, worn asphalt 0.12. Values can be found from wikipedia https://en.wikipedia.org/wiki/Albedo
    albedo = 0.151

    # module elevation, measured from ground
    module_elevation = 8  # unit meters

    # dummy wind speed(meter per second) value, this will be used if wind speed from fmi open is not used
    wind_speed = 2

    # air temp in Celsius, this will be used if temp from fmi open is not used
    air_temp = 20

    #### OTHER PARAMETERS

    # "Europe/Helsinki" should take summer/winter time into account, "GTM" is another useful timezone
    # timezone is currently not utilized as it should due to plotting issues
    timezone = "UTC"

    # data resolution, how many minutes between measurements. Recommending values 60, 30, 15, 10, 5, 1
    # will interpolate if resolution is higher than 60(30 or 15 etc.) as 60 is what fmi open data is capable of.
    data_resolution = 60

    # Cache locally fetched fmi open data to avoid repeated downloads.
    use_caching = True  # value= [True] or [False] this variable toggles caching of fmi open data on or off

    ########### PARAMETERS FOR FMI INSTALLATIONS BELOW:

    # functions like this can be used for easily running the code for multiple installations
    # known location specific params:
    def set_params_helsinki(self):
        self.latitude = 60.2044
        self.longitude = 24.9625
        self.tilt = 15
        self.azimuth = 135
        self.rated_power = 21
        self.module_elevation = 17

    def set_params_kuopio(self):
        self.latitude = 62.8919
        self.longitude = 27.6349
        self.tilt = 15
        self.azimuth = 217
        self.rated_power = 20.28
        self.module_elevation = 10
