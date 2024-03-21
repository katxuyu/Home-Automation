# Now read current weather status
    url2= 'https://api.climacell.co/v3/weather/realtime'
    datalayers = ['temp', 'cloud_cover', 'humidity', 'precipitation', 'cloud_ceiling', 'surface_shortwave_radiation',
                  'wind_speed', 'baro_pressure']
    querystring = {"lat":"-33.86739", "lon":"151.17475", "unit_system":"si", "apikey":"9U22L870pxb6ilqSuN6RQOUQJaSIxg8Y",
                "fields": datalayers}
    r2 = requests.get(url2, params= querystring ) 
    if r2.status_code != 200:
        print("We have problem accessing Climacell API "+str(r2.status_code))
    else:
        #print("Climacell API is sweet "+str(r.status_code))
        data2 = r2.json()
        temperature = float(data2['temp']['value'])
        print('ClimaCell temp now is '+str(temperature))    
        humidity = float(data2['humidity']['value'])
        precipitation = float(data2['precipitation']['value'])
        cloud_cover = float(data2['cloud_cover']['value'])
        cloud_ceiling = float(data2['cloud_ceiling']['value'])
        radiation = float(data2['surface_shortwave_radiation']['value'])
        wind_speed = float(data2['wind_speed']['value'])
        baro_pressure = float(data2['baro_pressure']['value'])
        client.write_points(
            [{"measurement": "ClimaCell", "tags": {"Poll": "Realtime"},
              "fields": {"Temperature": temperature, "Humidity": humidity, "Cloud cover": cloud_cover,
                         "Cloud ceiling": cloud_ceiling, "Radiation": radiation, "Precipitation": precipitation,
                         "Wind speed": wind_speed, "Baro pressure": baro_pressure }}]
        )