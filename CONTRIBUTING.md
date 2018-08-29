# Maze Pro Contribution Guidelines

## Table of Contents

## Issues
Issues are the key github feature used to manage the progress and direction of work on the project. The use of issues is intended to both provide those working on an issue with clear goals and an opportunity for discussion regarding the direction of the project. Issues should be atomic, describing a single task to accomplish.

### Issue Labels
Labeling an issue is an important part of managing the project. Issues should include labels tieing the issue to a specific piece of the overall project, and signal what kind of work the issue encompasses.

### Issue Format
An issue should include:
- A title clearly signaling the issues intent
- A summary outlining the purpose of the issue
- A description of the methods, and concepts needed to solve the issue
- A clear concise goal to meet in order to close the issue

## Milestones
Milestones have two main uses in this project. Some milestones exist to outline project requirements, and track large scale project progress over time, while others have a shorter life span batching related issues in a way to smooth the transition towards a pull request.
Milestones should describe a higher level problem then an individual issue could, and require multiple issues to complete.

Using a milestone can simplify the process of generating a pull request by grouping all of the issues needed to complete a specific feature before it is merged into the master branch. However in keeping with the monorepo philosophy **milestones should never keep completed code from merging into the master branch.**

## Projects
The projects feature on github is used to track what everyone is currently working on, what has been completed, and what is in the pipeline. The main maze pro project is structured using a TODO of issues not currently being worked, currently working on columns for each member of the group, and a single done column containing completed issues that have not yet been merged into master. Additional projects can be made arbitrarily if they can be used to improve an individual or teams workflow.

## Workflow
The development cycle on this project:

Generate issues -> create issue specific branch -> commit code referencing issues -> generate unit tests for all written code -> close issue -> pull request -> review -> merge -> delete branch -> generate issues. Within this workflow issues guide work towards a completed pull request which can be made from a single issue or group of issues associated with a milestone.

## Tests
Tests are used to ensure that code being merged into the master branch does not break existing code and provides a heuristic for the readiness of new code for use in the project. Testing should strive for 100% code coverage using a combination of unit tests and randomized end to end tests. Testing serves a dual purpose in ensuring code correctness and as a form of documentation. Tests should provide insight into how something works, and what its intended purpose is.

### Unit Tests
Pytest is used as the testing framework for this project and unit tests should make use of the robust pytest features. Fixtures should be used extensively to pre construct tests separating the requirements to build a test case from the actual logic of the test. Unit tests should be relatively atomic loosely adhering to the principle of one assert per test. Features should contain unit tests on well formed inputs as well as error handling / bad inputs. 

### End to end tests
End to end tests should incorporate random elements and used to tests the pipeline between features. As features interconnect end to end tests should test the correctness of input/ouput between features in a way that unit tests cannot achieve. Where the unit test tests a single feature in an isolated way, end to end tests are intended to ensure that outputs from one feature are well formed inputs to another within long chains of such interconnected features. 

## Commits
Commits should be atomic while providing a complete working addition to the code base. While individual commits can be added to a separate branch without additional unit tests, prior to closing an issue / generating a pull requests all committed code must include unit tests that covers additions / changes.

### Messages
A commit message needs to provide enough context for what was done without being overly robust. Commits should _always_ reference issues in order to assist in adding this context. A commit message title should reference an issue and states what the commit accomplishes using descriptive language rather then imperative language. The body of a commit should enumerate every change succinctly with no hidden alterations to the code base. 

### Tagging issues
Github provides a mechanism to easily attach commits to issues using issue numbers. This feature should be used as much as possible to lend conextual details to commits without bogging down the commit message itself. Reference [issues 2.0](https://blog.github.com/2011-04-09-issues-2-0-the-next-generation/#commits--issues) for details on incorporating issue mentions in commits.

## Pull Requests
A pull request signals that an issue, or milestone branch is ready to be merged into master. The pull request is a final opportunity to review code prior to changing the master branch, and should by generated only when committed code is of a high enough quality to be in production code. 

### Checklist
- [ ] 100% coverage with unit tests
- [ ] Passing all tests in project, and new tests
- [ ] Code is fully documented
- [ ] Code comments are free of spelling / grammar / style errors
- [ ] No pylint warning
- [ ] All issues referenced by commits are closed by the pull request

### Review Process
Before merging code into the master branch pull requests should be reviewed by someone other then the person generating the request. When reviewing a pull request any issues with documentation clarity, test coverage, and code issues should be flagged. When all reviewed suggestions have been addressed the reviewer should mark the pull request as reviewed and allow the pull request to be merged by the originator. 

## Style Guide
The [google python style guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md) is written down, exhaustive, and extendible. It will be used as a somewhat strict guideline, although readability / clarity should be paramount. If deviations from this style guide are warrented, mention in pull request why the alteration to the style guide was needed.