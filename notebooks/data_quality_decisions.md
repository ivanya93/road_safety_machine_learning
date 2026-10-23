## Data quality decisions

### Invalid coordinates

Three accidents have a location that cannot be in Brazil:

| Date       | Latitude | Longitude | Where that is                                      |
|------------|---------:|----------:|----------------------------------------------------|
| 2017-01-02 |        0 |         0 | Atlantic Ocean off Africa (a typical "empty" default value) |
| 2017-01-07 |       13 |        40 | Ethiopia                                           |
| 2017-01-07 |      −85 |       −40 | Antarctica                                         |

**Decision:** these 3 accidents are excluded from the regional data. Their region is found from the coordinates (nearest reference city), and a point outside Brazil would be assigned to a region at random. Only 1 of the 3 had victims, so the effect on the daily counts is negligible.

### Implausible `km` values

`km` is the position of the accident along the highway. Half of the values are below 202 km and 99.9% are below about 1,033 km, but 7 rows are above 4,500 km (up to 8,280 km). That is longer than any Brazilian federal highway, so these are typing errors.

**Decision:** the rows are kept and the values are left as they are. `km` is not a model input, and the region comes from the coordinates, not from `km`. A wrong `km` does not mean the accident did not happen, so the row still counts correctly. Removing these rows would lose real accidents for no benefit.

### Duplicate rows

There are 49 pairs of rows that are identical in every column (the `accident_id` we added is ignored for this check). All of them are from 2007–2014, none of them have coordinates, and 41 of the 49 are class 0 (no injuries).

**Decision:** the duplicates are kept. The source has no accident ID, so we cannot tell a double entry from two real accidents on the same stretch of road on the same day. None of the duplicates enter the model data (April 2018 onward, with coordinates), so removing them would not change any result.
