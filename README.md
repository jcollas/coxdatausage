# Custom Component Cox Data Usage
This is a custom_component for Home Assistant to create a sensor for data usage on Cox

You must add this to your `custom_components` folder with the directory and file structure provided!

Cox Data Usage Sensor

Example config:
```
- platform: Cox
  name: Cox Data Usage
  username: !secret cox_username
  password: !secret cox_password
```
