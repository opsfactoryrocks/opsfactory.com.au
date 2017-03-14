Title: Keep Your Tools Simple
Date: 2017-03-14
Category: Tools
Tags: tools, development, systems
Slug: simple-tooling
Authors: Michael Crilly
Summary: use the right tool for the one job and you'll have an easier time

As time goes on in our industry more tools, frameworks, and libraries make themselves known and some even go on to become popular. In rare cases, a few become industry standard tools and appear in job advertisements and demand high salaries for expertise. I use a few select tools on a near daily basis and they definitely count among the (fast becoming) industry standard: Ansible and Terraform.

Ansible is an excellent tool for configuration management tasks at the OS level and beyond. It's core utilities offer stable management of files, users, packages, services, firewalls, and much more.

Terraform is my tool of choice for anything below the OS and beyond. It's HCL language is easy to write and very descriptive. It's AST offers a great advantage over using Ansible for the same infrastructure tasks, and it supports a large range of providers from compute resources to DNS.

To keep things simple, I leave Ansible out of the infrastructure equation and I keep Terraform away from the OS. Other people don't follow this methodology, instead favouring Ansible as their goto infrastructure building and management tool as well as their OS and software configuration management utility. It's their kitchen sink with a built in espresso machine and pencil sharper.

## But, but...
There are no buts. One tool for one job. If you one tool does one job and it's refined and sharper to do that job well over the course of years, it excels at that one job.

If you were to use Terraform to not only build your EC2 instances but also use whatever native methods is has available for configuring the OS' state, you would have one HCL code base. This code base would build your servers and configure them too. That would be nice, but alas **Terraform wasn't designed** to be a CM tool. It's designed to build the data centre level resources.

Now take Ansible and apply the same logic: use it to build out your EC2 instances and configure the base OS state. Actually, Ansible has both forms of functionality native to it, because it has (none core) AWS modules and (core) modules for state management. Now you'd have a large collection of state files consisting of YAML. Problem is Ansible's not really designed for or good at managing infrastructure. It's designed to manage state at the OS and above, and it's very good at it.

Just because I CAN weld a tin opener to the side of my oven, it doesn't mean I should. And if someone sneaks into my house and does it for me (please don't), I still aint going to use it (the tin opener that is. I'll still use the oven.)

### Ansible's Core Purpose
Time and effort has been put into Ansible since its inception. It's good at supporting very low level OS tasks such as package management, services, users, files and file systems, processes, disks, and more. These modules are rock solid because they've been developed and tested a lot.

The infrastructure modules are extras and they've kind of been bolted onto the side in recent years. They certainly work -- I know they work, I've used them -- but a lot of logic has to be build around them to get the same, but **much weaker**, functionality that a purpose built tool gives you.

An analogy might be a hammer that has a screw driver duck taped onto the side of it. Now you can throw away your individual hammer and spanner, and simply buy the all new Spammer (what a name!) Just keep in mind that you'll need to develop some extra dexterity whilst operating the Spammer, and safety can go out the window too.

### Terraform's Core Purpose
HashiCorp developed Terraform with the data centre in mind. They wanted it to manage infrastructure and nothing more. They've achieved this objective very well and you won't find HashiCorp adding features just because they can - it's a tool for doing one job and doing it really well.

If Terraform is the hammer, then Ansible is your paint brush, roll of wallpaper, and maybe even your furniture.

## Cleaner, Simplier Code
When I keep my Ansible Roles and Playbooks all nicely separated, and my state clear of any extra modules, I end up with a very simple configuration base to work with. The Roles are simple, the state is simple, everything is simple.

By keeping my Terraform code just about infrastructure, the code base is simple and easy to follow. The two can be connected in many ways, but keeping to one task per tool I achieve what I believe to be nirvana in the DevOps space.

Reading my Ansible state, Roles, and so on, is easy. The logic is kept to a minimum where possible and the Roles are a breeze to read.

Reading my Terraform code base with its modules and such is easy too. It's not hard to find what you need and understand what's happening.

## It's all in the AST
Ultimately though, what really does it for me is Terraform's Abstract Syntax Tree. This is one of its killer features and it blows Ansible (and Chef and Puppet, or any CM tool for that matter) out of the water when it comes to infrastructure state management.

In short, I can define some state locally, apply it remotely and even the smallest of changes can be pointed out with a simple `terraform plan`. I get a report telling me exctly what has changed, regardless of the resource or detail I'm changing, and what has to be done to achieve the desired state. **This is important** because I'll be able to understand if an EIP must be destroyed and recreated due to my change; an EBS volume must be detached and reattached because a bit was flipped; or if a DNS record will change because of an EC2 instance being destroyed.

**Ansible doesn't do this.**

When something changes in my YAML files, Ansible simply checks if the remote state matches what I have locally and if not, it changes it. Well actually that's kind of fine... sort of.

If I have a single file which is critical to the operation of a server, let's say the `/etc/hosts` file, and I change it through Ansible's `lineinfile` module, what check is done to ensure something else I'm configuring with Ansible won't break? If I'm defining a DNS lookup in that file for `master-database` and then in the configuration for a Wordpress role I'm setting the DNS to point at that line, my future change to remove this line isn't picked up. My Wordpress just went down.

When using Ansible's mildly "OK" AWS modules, what check is done to confirm the EIP attached to an EC2 instance should be released if the EC2 instance is deleted? If I run `ansible` and do an adhoc command to remove the EC2 instance, any logic inside the Playbooks and Roles goes out the window. One can only hope the AWS API will complain about the EIP and save the day. That's not an ideal safety net.

## Do it anyway
Ultimately whatever works for you should be kept in place. I'm certainly not asking anyone to change the way they work or stop what they're doing. This is just food for thought; something to think about, or not; and maybe just discuss among your local peers.

## [KISS](https://en.wikipedia.org/wiki/KISS_principle)
Use purpose built tools. Stop trying to make one thing do everything for you. Your life will get easier, I promise.