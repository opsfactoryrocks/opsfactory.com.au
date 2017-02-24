Title: Ansible Roles and Default Variables
Date: 2017-02-24 1800
Category: Ansible
Tags: ansible, confmg
Slug: ansible-roles-and-default-variables
Authors: Michael Crilly
Summary: Write Roles like you're writing a function in a library.

Roles are a critical part of Ansible: they wrap up functionality into a nice little parcel which is easy to manage, maintain, [version control](https://git-scm.com) and share. Adhoc commands and a directory full of Playbooks can of course be very useful, but Ansible really shines when Roles are introduced to a code base. Writing a Role well only requires following some basic best practices.

Let's start off by looking at default variables for a Role.

## function(a, b, c);
When you provide someone with a Role, they will very likely need to customise its behaviour to suit their own requirements. It's the same when you execute a function in some library: the function or method offers you some algorithm that solves a problem, but you must provide the inputs. Your Role solves some infrastructure level problem, you just have to provide the correct inputs.

**A Role's variables are like a function's parameters: they're the interface to your solution.**

What this means for you as a Role developer is simple: ensure you're providing default variables for all inputs and all the external data the Role needs, allowing it to execute without errors. This means allowing it to execute cleanly, end-to-end, without errors or warnings, whether or not the state results in valid operations.

### Edge Cases
With functions, most of the parameters aren't optional or ship with default values. In Python you do often see default values for optional variables, but it's not always the case. If you find you're writing a Role that can't work with a default value and simply must be given a value: **document this fact in the `README.md` file**

I understand not every situation allows you to develop Roles in such a way, and that's fine. Just try your best to write code that the next person will enjoy working with.

## Validation
Because a Role with default variables (that haven't been overridden) can execute against live infrastructure without reporting any problems, as discussed above, you could be forgiven for making the assumption the infrastructure was setup and placed into a desired state. Without testing this assertion, however, you never really know the state of your infrastructure.

This is why testing is important when developing a Role. It's why we use [Molecule](https://github.com/metacloud/molecule) for testing Roles during development and for idempotence; and it's why we use [Gos](https://github.com/aelsabbahy/goss) to ensure when we feed in inputs to our Roles the results that come out the other end are valid.

Software engineers and developers test their code, **so you should too.**

## Namespacing
When writing your default variables, namespace them. Ansible's memory model for variables is essentially **flat and global.** That means you could potentially run the risk of causing mahem if you have a variable to your Role called `java_version` which is then used by a second Role in your Play(book).

When you introduce a namespace to your Role's variables, you remove this risk. And namespacing isn't technically challenging or difficult, it's just a simple rule to follow: use the Role's name in the variable.

If we assume a Role called `mysql`, then we can assume a `defaults/main.yml` that might look a bit like this:

```yaml
---
mysql_version: 5
mysql_data_directory: /var/data/mysql
mysql_server_only: false
```

And so on.

## Documentation
The final point I want to touch on is documentation. When you provide default variables in your Role, you provide a form of documentation. It's documentation in its simpliest form, but it is documentation. You could even be forgiven for omitting them from the `README.md` file if you comment them sufficiently. 

I'll talk about documentation in another post.

## In Summary
When writing a Role, provide and namespace your default variables. Also allow the Role to be execute end-to-end without overriding any of the default variables, and result in a green screen.