## ItzMenu

[![ItzMenu Build](https://github.com/Louuke/ItzMenu/actions/workflows/build.yml/badge.svg)](https://github.com/Louuke/ItzMenu/actions/workflows/build.yml)

ItzMenu is a distributed service that queries the weekly menu of a Sodexo canteen and turns it into a structured 
JSON object. It provides a REST API to access the current and past menus. The service is written in Python and
uses the FastAPI framework.

The collected data is intended to be used by other services to provide additional functionality, 
such as categorizing the menu items by their diet type using machine learning.

### Project Structure

- `itzmenu/`: The main package of the project.
- `itzmenu/api/`: contains Pydantic models for the API.
- `itzmenu/client/`: contains the client to post the menu to the service.
- `itzmenu/extractor/`: contains the extractor to scrape the menu data.
- `itzmenu/service/`: contains the FastAPI service.