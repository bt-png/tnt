
For storing Tip Specific Data, values should be stored within the st.session_state['tipddata'] dictionary.

The st.data_editor stores differently, and needs to be pushed/pulled by name. This is done under company.publish

Any time an update is made, the st.session_state['updatedsomething'] variable should be set to True

# Tipping variables contained within st.session_state['tipdata']
## Variables updating via sync.synctipsdata
*** Items referencing 'Garden FOH, FOH' are indexed by clientGetValue(st.session_state['company'], 'tippools')
These can be written directly with publish
| key | file | type | description |
| --- | --- | --- | --- | --- |
| Total Hours Worked | tipping0 | float | hrs |
| Employees Worked | tipping0 | list | employee names |
| Available Work Positions | tipping0 | list | working positions (used and override)
| Total Wages Paid | tipping0 | float | $ |
| Total Pool | tipping0/tipping2 | float | $ |
| Extra Garden Tip | tipping0 | float | $ |
| Tip Exempt Employees | tipping1 | list | employee names |
| Tip Elligible Employees | tipping1 | list | employee names |
| Base Garden Tip | tipping2 | float | $ |
| Helper Pool | tipping2 | float | $ |
| Chef Percent | tipping2 | int | % (100 base) |
| Chef Pool | tipping2 | float | $ (Calculated Value based on Chef Percent and Remaining Tip Pool) |
| Regular Pool | tipping2 | float | $ (Calculated Value) |
| tippool | tipping2 | dict | {'Garden': 100, 'Regular': 50, 'Helper': 25, 'Chefs': 75} |
(del) | tippoolpercents | tipping2 | dict | % of five available tip pools |
| tippool_g1 | tipping2 | int | % 0 index of tipping pools (Garden FOH) |
| tippool_g2 | tipping2 | int | % 1 index of tipping pools (Garden Host) |
| tippool_f1 | tipping2 | int | % 3 index of tipping pools (FOH) |
| tippooltotals | tipping2 | dict | {"Garden FOH": 59.85, "Garden Host": 11.4, "Garden BOH": 23.75, "FOH": -1879.02, "BOH": -967.98} |
| tippoolsumhrs | tipping2 | dict | {"Garden FOH": 0, "Garden Host": 0, "Garden BOH": 0, "FOH": 27.6, "BOH": 0} |
| tippoolhourlyrates | tipping2 | dict | {"Garden FOH": 0, "Garden Host": 0, "Garden BOH": 0, "FOH": 11.765217391304349, "BOH": 0} |
| tiptotals | tipping2 | float | $
| helperEmployeeNamepool | tipping2 | list |  |


# Tipping variables contained within st.session_state[key] that need to be popped to st.session_state['tipdata'][key]
## Dataframes requiring direct updating. Add to company.publish()
Prior to publish, duplicate the individual tables into ['tipdata] using the same key
When pulling new information from the server, each of these should be popped from the ['tipdata'] to st.session_state using the same key
| widgetkey | file | description |
| --- | --- | --- | --- |
| GardenDates | tipping0 | Dates from tipping pool where tips should be associated to the garden pool 
| work_shifts | tipping0 | QTY of Worked shifts by Employee
| chefEmployeePool | tipping1 | QTY of Worked shifts for Employees that are chefs -> changes are pushed to 'work_shifts'
| ORIGINAL_WorkedHoursDataUsedForTipping | tipping1 | Tip Elligible Work Sessions - No changes Applied
| DEFAULT_WorkedHoursDataUsedForTipping | tipping2 | Tip Elligible Work Sessions - Default work shifts applied
| WorkedHoursDataUsedForTipping | tipping2 | Tip Elligible Work Sessions - Default and manual work shifts applied
| RevisedDefaultWorkPositions | tipping2 | update the default position splits
| default_possplits_summary | tipping2 | summary of default movements
| RevisedWorkPositions | tipping2 | move hours from position to position
| ALL_RevisedWorkPositions | tipping2 | manual and default revisions to worked hours
| Helper Pool Employees | tipping2 | DataFrame selecting if helpers should remain in tipping pool
| housetipsforemployees | tipping2 | All employees worked, filtered by active tip elligibility
| df_tipssum | tipping2 | Condensed summation of tips by Employee Elligible. sliced from WorkedHoursDataUsedForTipping
