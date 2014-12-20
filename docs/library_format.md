## Directories

* `originals/`
  - `2014/`
    + `2014-12-14 Some photos/`
      * `cat.jpg`
      * `dog.jpg`
      * `bad.jpg`
      * `metadata.yaml`
* `events/`
  - `2014/`
    + `2014-01-01 New Year 2014/`
      * `~2014-01-01 00.14.23 I are Serious Cat.jpg`
      * `~2014-01-01 00.43.16.jpg`
* `tags/`
  - `new year/`
  - `family/`
  - `cats/`
    + `~2014-01-01 00.14.23 I are Serious Cat.jpg`
* `people/`
  - `Serious Cat/`
    + `~2014-01-01 00.14.23 I are Serious Cat.jpg`
* `library.yaml`


## meta.yaml file format

    all:
      event: New Year 2014
      event_date: 2014-01-01
      tags:
        - new year
        - family
    cat:
      title: I are Serious Cat
      tags:
        - cats
      people:
        - Serious Cat
    bad:
      hidden: true
