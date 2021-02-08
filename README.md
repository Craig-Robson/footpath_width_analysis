# footpath width analysis
This code repository attempts to provide a method to produce estimates for the width of polygons it is passed, in particular polygons representing roadside pavements and paths. Additional functions are also provided which allow summaries to be produced at neighbourhood level. Initial results can be seen at https://craig-robson.github.io/pavement_maps/

The code contained within for estimating polygon widths has been adapted from another repository (https://github.com/tomalrussell/pavementwidths-gb), which itself was adapted from a further repository (https://github.com/meliharvey/sidewalkwidths-nyc). 

##

## api_config.ini
A config file is used to store the url for the API and the username and password for the this. It should have the following structure:  
[API]  
url=www.url  
username=username_for_api  
password=password_for_api  