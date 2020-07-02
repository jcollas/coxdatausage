# This has been archived and no longer functions as designed. Needs the API updated.

## Custom Component Cox Data Usage
This is a custom_component for Home Assistant to create a sensor for data usage on Cox

### Installation

Copy the folder `coxdatausage/` folder to `<config_dir>/custom_components/`.

Add the following to your `configuration.yaml` file:
```yaml
- platform: Cox
  name: Cox Data Usage
  username: !secret cox_username
  password: !secret cox_password
```
