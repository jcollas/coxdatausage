
# Custom Component Cox Data Usage

This is a custom_component for Home Assistant to create a sensor for data usage on Cox.

This has been updated to work properly with the new Cox Okta authentication API.

### Installation

Copy the folder `coxdatausage/` folder to `<config_dir>/custom_components/`.

Add the following to your `configuration.yaml` file:
```yaml
- platform: coxdatausage
  name: Cox Data Usage
  username: !secret cox_username
  password: !secret cox_password
```
