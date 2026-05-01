from services.data_service import DataService

ds = DataService()

if ds.df_standardized is None:
    print("ERROR: Data failed to load")
else:
    print("Commodities:", ds.get_commodities())
    print("Total rows:", len(ds.get_all_data()))
    mango = ds.get_commodity_data('Mango')
    if mango:
        print("Mango rows:", len(mango))
        print("First:", mango[0])
        print("Last:", mango[-1])
    else:
        print("ERROR: No Mango data found")