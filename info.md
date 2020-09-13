
# Cox Data Usage

An integration which creates a sensor for data usage on Cox.

This has been updated to work properly with the new Cox Okta authentication API.

Add the following to your `configuration.yaml` file:
```yaml
- platform: coxdatausage
  name: Cox Data Usage
  username: !secret cox_username
  password: !secret cox_password
```

This creates a new sensor called `sensor.cox_data_usage` whose value is the number of GB consumed so far.  

The following attributes are available on the sensor:

Attribute | Description
--- | ---
Used data | Amount of data used in GB
Total data | Total amount of data plan in GB
Days this month | Number of days in the plan cycle
Days Left in Cycle | Number of days left in the plany cycle
Percentage Used | Percentage of data used 
Average GB Used Per Day | Average per day
Average GB Remaining Per Day | Average remaining per day