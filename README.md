qa-openstack-tempest
====================

tempest based openstack test suites, based on branch tempest/essex

1. Put the package in the tempest dirctory:
```
   tempest/
    ├── etc
    ├── tempest
    ├── ...
    └── qa-openstack-tempest
```

   Make sure both tempest and qa-openstack-tempest have the same git branch(latest version is grizzly)

2. Configure file 'config' by your test requirement

3. In the object directory run: ./run.sh

4. To run test case individually, please process like this:
   # source config
   # ./test/<test case>
