import arcpy


# Dictionary storage for the environment parameters
env_params = {
    'workspace_path': r'.\ArcGIS Workshop Demo.gdb',
    'coordinate_system': 'WGS 1984'
}

# Storage variables for data imported from ArcGIS
medical_facilities = []
my_home = None


'''
    Sets up the arcpy environment;
        path to geodatabase,
        and setting the coordinate system
'''
def setup():
    global env_params

    arcpy.env.workspace = env_params['workspace_path']
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(env_params['coordinate_system'])

    print('Environment is setup.')


'''
    Imports the data from ArcGIS and stores it in the global storage variables
'''
def read_data():
    global medical_facilities
    global my_home

    feature_classes = {
        'medical_facilities_class': 'OSM_Medical_Facilities_AS_Cl1',
        'my_home_class': 'MyHome'
    }

    try:
        for row in arcpy.da.SearchCursor(feature_classes['medical_facilities_class'], ['SHAPE@']):
            medical_facilities.append([row[0]])

        for row in arcpy.da.SearchCursor(feature_classes['my_home_class'], ['SHAPE@']):
            my_home = row[0]

        print('Data reading is complete.')
    except Exception as e:
        print(e)


'''
    Finds the closest requested number of facilities from my_home:
        1. calculate the distance from my_home to each medical facility
        2. Sort the facilities in ascending order according to the distance
        3. Take the desired number of facilities from the top of the sorted facilities list
'''
def find_closest(desired_num_of_facilities):
    global medical_facilities
    global my_home

    for medical_facility_index in range(len(medical_facilities)):
        distance_from_my_home = my_home.distanceTo(medical_facilities[medical_facility_index][0])

        medical_facilities[medical_facility_index].append(distance_from_my_home)

    # Sort the list of lists according to the second item in each list
    medical_facilities.sort(key=lambda x: x[1])

    if desired_num_of_facilities <= len(medical_facilities):
        print('Closest medical facilities found.')
        return medical_facilities[:desired_num_of_facilities]
    else:
        print('There does not exist the requested number of medical facilities.')
        return None


'''
    Save the resulted list of medical facilities into a new feature class
'''
def save_results(resulted_facilities):
    global env_params
    results = 'Results'

    if not arcpy.Exists(results):
        arcpy.CreateFeatureclass_management(env_params['workspace_path'], results, 'POINT')
    arcpy.TruncateTable_management(results)

    results_cursor = arcpy.da.InsertCursor(results, ['SHAPE@'])

    for resulted_facility in resulted_facilities:
        results_cursor.insertRow([resulted_facility[0]])
    del results_cursor

    print('Results saved in geodatabase.')


if __name__ == '__main__':
    setup()
    read_data()
    resulted_facilities = find_closest(5)
    if resulted_facilities is not None:
        save_results(resulted_facilities)