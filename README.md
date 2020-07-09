# Police Accountability Impactathon Project

1. [Overview](#overview)
1. [Description of Data](#data)
1. [Scripts](#scripts)
1. [Organization of Project](#project_org)

## <a id='overview'>Overview</a>

Law enforcement offices in the United States are not subject to the same checks and balances as regular citizens.
Practices such as
[qualified immunity](https://en.wikipedia.org/wiki/Qualified_immunity) and
[civil asset forfeiture](https://en.wikipedia.org/wiki/Civil_forfeiture_in_the_United_States)
have led to abuses of power by law enforcement agencies including violence against citizens.
The aim of this project is to improve accessibility of information about:
* government offices and officials that may be able to influence laws in order to hole law enforcement equally accountable
* lawyers and law offices that practice in the area of civil rights in case you or someone you know has their rights infringed upon by law enforcement
* law enforcement agencies themselves - as it may be valuable to communicate directly with your local agency

## <a id='data'>Description of Data</a>
Law enforcement agency data was principally sourced via wikipedia.

Lawyer information was principally sourced from a number of law firm advertising websites that allow you to search by area of expertise and location.

Government information is yet to be sourced.


## <a id='scripts'>Scripts</a>

_All scripts should have a `--help` option which provides a concise description of what the scripts purpose is._

`add_urls_to_depts.py` - Given a db with law enforcement agency data loaded with possibly missing URLs, run a search for the dept name and state/location and add the top result as the URL.

`export_states_to_csv.py` - Given a db with law enforcement agency data loaded, export to flatfiles partitioned by state.

`get_lawyer_info.py` - Run a series of searches for lawers in civil rights practice currently saving to S3, TODO: import that data from S3.

`import_from_csvs.py` - The mirror of export states to csv, this will drop the local tables and import from the csvs in the data dir.

`import_states_from_wikipedia.py` - This is what was initially used to get law enforcement agency info from wikipedia.


## <a id='project_org'>Organization of Project</a>

```
├── data - parent of all data files (trying to avoid putting things on s3 in order to make things as portable as possible)
│   ├── departments - information about law enforcement agencies - as csv, partitioned by state, imported by `import_from_csvs.py`
│   └── pop_by_zip_only.csv.xz - zipcode and population (as of 2000) for united states zipcodes - thought being when we have to prioitize resources targeting higher population densities can maximize effectiveness.
├── nginx - honestly all that lives here now is the nginx.conf file, maybe should move the root of the static dir in here
├── static
│   └── html - believe you can drop static files here in order to have nginx serve them directly
└── webapp
    └── app - simple python app in order to actually do a little bit of processing of a request
```

`makefile` - single point of entry for user/developer - `make up` should create & start your db, import the data and start nginx and a python webserver.
