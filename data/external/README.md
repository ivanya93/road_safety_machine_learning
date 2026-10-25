# External data

## brazil_states.geojson

Borders of Brazil's 27 states, used to draw the forecast maps per macro-region (`03_Modelling.ipynb`, section 9.10).

- **Source:** `public/data/brazil-states.geojson` from [codeforgermany/click_that_hood](https://github.com/codeforgermany/click_that_hood) (MIT licence), downloaded on 25 Oct 2026.
- **Simplified for this project:** every 4th point kept, coordinates rounded to 0.01° (about 1 km). That is enough for a map of the whole country, and the file goes from 3.3 MB to 0.3 MB.
- **Added column `region`:** the macro-region, from the first digit of the IBGE state code (1 = Norte, 2 = Nordeste, 3 = Sudeste, 4 = Sul, 5 = Centro-Oeste).
