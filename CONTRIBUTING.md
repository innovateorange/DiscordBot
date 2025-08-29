<!-- CONTRIBUTING.md is based on the provided in the Red Queen Repo: https://github.com/Qiskit/red-queen/blob/a9f396b16c88cea9c9987cd379526c0624e22323/CONTRIBUTING.md -->

# Contributing

First read the overall project contributing guidelines. These are all
included in the ReadMe file of this repo:

<https://github.com/innovateorange/DiscordBot/blob/ec161ab7b4d38fab5db17f62c353e9d673e6fbde/README.md>

## Contributing to Discord Bot Project


### Creating a new issue

This is where contributions begin within our project.

We use custom issue templates to streamline how you report bugs, suggest new features, or track tasks. To create an issue within the repository:

1. Navigate to the main page of the repository.
2. Under the repository name, click **Issues**.
![Screenshot of Issues tab](https://github.com/user-attachments/assets/de42d43f-b0ea-4e4d-a5c9-b5bafaa30cec)
3. Click **New Issue**
![Screenshot of New Issue button](https://cdn.discordapp.com/attachments/280059731249201164/1362294261743091774/Screenshot_2025-04-17_011024.png?ex=6801dee6&is=68008d66&hm=f75358fbe9364f0603011d762c8aca450227d431f1e3133ddf5f60cf54feccc2&)
4. Choose an issue template that is relevant to the task you are creating based on the following:
![Screenshot of Issue Templates](https://cdn.discordapp.com/attachments/280059731249201164/1362297577982136420/image.png?ex=6801e1fc&is=6800907c&hm=43d4fde8f4efb9f2c5938a6a46f568c3e4335fbf936b6513f9af51353f9bd45d&)

- **Bug Report**

  Use this template if something isn't working as expected. You'll be prompted to
  - Describe what happened and what you expected.
  - Outline the steps to reproduce the issue.
  - Optionally attach screenshots or logs.
- **Feature Request**

  Use this when suggesting a new idea or improvement. You'll be asked to:
  - Describe the feature and its purpose.
  - Explain the motivation or problem it solves.
  - Suggest possible alternatives or solutions.

> [!NOTE]
> For all other issue types (e.g., documentation, research, workflows), please fill out a blank issue stating the information needed to resolve the task.

These templates ensure that issues are organized and easier for maintainers to address. Please fill them out thoroughly!


### CI/CD Jobs

Time to get a bit more technical. [CI/CD](https://github.com/resources/articles/devops/ci-cd) means Continuous Integration and Continuous Deployment and serves as our way of implementing defensive programming in our development workflow. (Continuous Integration and Continuous Delivery/Development) Jobs are crucial to ensuring that our codebase remains clean, reliable, and secure. These automated processes help catch formatting issues, typos, and code that doesn't follow our project's conventions before it makes it to our main branch. They also catch any vulnerabilities in our code early.
In this project, we use three main CI/CD jobs to help uphold the principles of defensive software development:

- `python-package.yml`  
This workflow installs project dependencies, runs linting tools, and executes our unit tests. It's our first line of defense against breaking changes and helps us make sure nothing sneaky slips through when new code is added.  

  >![NOTE]This workflow runs every time there is a new pull request that is attempting to push to main

- `codeql.yml`  
CodeQL analyzes the codebase for potential security vulnerabilities. It searches for code patterns that could lead to bugs or exploits and helps catch more significant issues that traditional testing might miss.
  
  >![NOTE]This workflow runs everytime there is a new pull request that is attempting to push to main

- `dependabot.yml`  
Dependabot automatically monitors our dependencies and opens pull requests when updates are available. This helps us stay current with library versions and patch known security issues before they become an issue.

> This document will be updated based on the needs of the team
>
> -[Caleb](https://github.com/Lementknight)
> -[Andrew](https://github.com/andewmark)