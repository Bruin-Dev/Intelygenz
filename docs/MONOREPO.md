<div align="center">
<img src="https://media.licdn.com/dms/image/C4E0BAQHrME9aCW6ulg/company-logo_200_200/0?e=2159024400&v=beta&t=6xMNS1zK1F8asBlM16EzbJ4Im7SlQ8L7a7sgcaNzZQE"  width="200" height="200">
</div>

# Monorepo

> In revision control systems, a monorepo (syllabic abbreviation of monolithic repository) is a software development 
> strategy where code for many projects are stored in the same repository. [Wikipedia](https://en.wikipedia.org/wiki/Monorepo)

## Advantages

+ **Simplified organization**: The organization is simplified separating all the projects(called modules) in different folders
that are stored in the root folder of the repository.
+ **Simplified automation**: The automation gets easy with this approach, each time the repo has a commit in develop or master
the automation will deploy all the necessary parts of the app to make it work correctly.
+ **Refactoring changes**: When a project has a dependency with another in the monorepo, the changes are easier to be made.
+ **Atomic commits**: When projects that work together are contained in separate repositories, releases need to determine which 
versions of one project are related to the other and then syncing them.
+ **Collaboration across team**: The integration between projects will be easier thanks to the branches strategy
+ **Single source of truth**: Like a developer you'll find all the available code, automation and documentation in the same place.

## What is not a monorepo about

+ Monorepo is not the same that Monolith. Monolith is huge amount of coupled code of one application that is hell to maintain.

+ This is not only a repository, it's a sum of good practices between automation, code and documentation.

---
With passion from the [Intelygenz](https://www.intelygenz.com) Team @ 2019