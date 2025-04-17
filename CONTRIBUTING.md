<!-- CONTRIBUTING.md is based on the provided in the Red Queen Repo: https://github.com/Qiskit/red-queen/blob/a9f396b16c88cea9c9987cd379526c0624e22323/CONTRIBUTING.md -->

# Contributing

First read the overall project contributing guidelines. These are all
included in the ReadMe file of this repo:

<https://github.com/innovateorange/DiscordBot/blob/ec161ab7b4d38fab5db17f62c353e9d673e6fbde/README.md>

## Contributing to Discord Bot Project

### Style and lint

Discord Bot Project uses two tools to verify code formatting and lint checking. The
first tool is [black](https://github.com/psf/black) which is a code formatting
tool that will automatically update the code formatting to a consistent style.
The second tool is [ruff](https://github.com/astral-sh/ruff) which is a code linter
which does a deeper analysis of the Python code to find both style issues and
potential bugs and other common issues in Python.

You can check that your local modifications conform to the style rules
by running `nox` which will run `black` and `ruff` to check the local
code formatting and lint. You will need to have [nox](https://github.com/wntrblm/nox)
installed to run this command. You can do this with `pip install -U nox`.

>[!NOTE]
>If black returns a code formatting error, you can run `nox -s format` to
automatically update the code formatting to conform to the style. However,
if `ruff` returns any error, you will have to resolve these issues by manually updating your code.

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

### Creating a new branch

When you want to contribute to the Discord Bot Project, you will need to create a new branch where you will be staging your changes.

You can do this by running the git checkout command:

```bash
git checkout -b <new_branch_name>
```

> [!TIP]
> Note that this command creates a branch base on the branch that you are currently in, so please make sure that you are on the main branch when you are making a new branch.
>
> You can see which branch you are on by using the git branch command:
>
> ```bash
> git branch
> ```

Once you are ready to push your code to the branch that you created, you have to stage the changes.

### Staging your changes

First you need to add all your changes (deltas) to a git. [You can think of this as putting all of your work into an unmarked folder]

```bash
git add -A # This adds all of the files/edits that you have made 
```

After you add your changes to git, you need to sign it with a message [You can think of this as signing the folder with your name so we know whose work is in the folder]:

```bash
git commit -am "<Title of Change>\n <Rationale behind change>" # This command signs your changes
```

> [!TIP] You can think of your commit message as an email where you explain to your team the reasoning behind your changes. You don't need to explain you changes, your deltas are visable for any reviewers. The thought behind your changes should be clearly outlined in your commit.

After you sign your changes, you need to push your changes to your branch's upstream:

For first-time commits to branch:

```bash
git push -u # This command creates an upstream version of your local branch 
```

>[!NOTE]
> The -u flag is important to track the initial tracking history of the branch itself. You're basically telling git: "Hey, from now on, whenever I'm on this branch, I want to link it to this branch on GitHub." Almost like saving contact information on your phone

For subsequent commits to branch:

```bash
git pull # Pulls changes from base repository 
git push # Pushes changes to upstream
```

### Creating a Pull Request Draft

Once you have established a upstream tracking for your the branch, navigate to the GitHub repository's `Pull requests` section. You should see a button that says `Compare & pull request`.

It should look similar to this:

![image](images/pull_request_ex1.png)

Press the `Compare & pull request` button, then you will be given the option to create a pull request in this screen:

![image](images/pull_request_ex2.png)

Click the dropdown menu of the `Create pull request` button:

![image](images/pull_request_ex3.png)

And then create a draft pull request. Now you can see if your changes pass the [CI/CD](https://github.com/innovateorange/DiscordBot/actions) checks. From here you can work on your changes until it is ready for review.

Before submitting your code for review, please ensure that you have completed the following:

- [ ] Ensure that your code passes all of the [CI/CD](https://github.com/innovateorange/DiscordBot/actions) checks
- [ ] You have added tests for any new features
- [ ] You have added documentation for any new features
- [ ] You have added a description of the changes you made in the pull request

> [!NOTE]
> If your pull request is missing any of the above, it will be converted back to a draft and will not be reviewed until the above conditions are met. This is to ensure we are following best practices for industry-ready code.

Once you have ensured that you have done all of the above, you can convert your draft to a pull request for review. You can do this by pressing the `Ready for review` button:

![image](images/pull_request_ex5.png)

Once you do that, you are ready for code review!

### Code Review

Congrats you have made it to the part where you interact with people! Code review is an opportunity for other people to review your changes and offer you feedback. It's important to make sure that you keep an open-minded in this process. Receiving feedback can be challenging initially, but with respectful communication it will help you gain the skills of a mature software engineer.

When it comes to code review, there are a few things that you should keep in mind:

- [ ] Be respectful and kind to your reviewers
- [ ] Be open to feedback and suggestions
- [ ] Be open to revising your code based on feedback.
- [ ] Be willing to ask questions if you don't understand something
- [ ] Be willing to offer feedback to others
- [ ] Be willing to help others if they are struggling with something
- [ ] Be willing to learn from others
- [ ] Be willing to share your knowledge with others

> [!NOTE]
> Code review is a two-way street. You should be open to receiving feedback, but you should also be open to giving feedback. If you see something that you think could be improved, please provide feedback respectfully. We want to make sure that we are creating a positive and inclusive environment for everyone.

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

By contributing to this repo, you're also contributing to the standard of quality. So, if the CI/CD workflow fails on your pull request, don't worry; it's just part of the process to help you (and the rest of the team) write better, more secure code.

> This document will be updated based on the needs of the team
>
> -[Caleb](@Lementknight)
