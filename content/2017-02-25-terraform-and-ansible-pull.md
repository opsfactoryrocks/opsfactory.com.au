Title: Terraform and Ansible Pull
Date: 2017-03-05
Category: Automation
Tags: ansible, confmg, terraform, infrastructure
Slug: terraform-and-ansible-pull
Authors: Michael Crilly
Summary: Pulling instead of pushing for self-provisioning systems is very powerful, especially without a centralised authority to maintain.
Status: draft

I was first introduced to Configuration Management via [Puppet](). I used it extensively at several engagements and it did the job rather well. The DSL was workable, writing modules was simple enough, and Puppet its self, as well as the projects around it ([Foreman]() and [Hiera]()) did a great job of making the whole state management process easier.

During that time I had also discovered and grew very fond of Ansible. It was quickly becoming the superior product from my perspective, primarily due to the simple integration and push (by default) based model. **I haven't touched Puppet for nearly four years.**

Although Ansible won out with its push model, time and time again I found managing inventories and executing tasks locally tedious. I often caught my self wishing I could actually just implement some centralised system that Ansible pulled from. I obviously knew of `ansible-pull`, but what would the architecture look like? How could I still get Ansible's frictionless push model integration into a network and still remove the need for dealing with inventories?

## A shell script
I eventually settled on a very simple but effective solution: a shell script executed on a new instance via the user data/[cloud-init](https://cloudinit.readthedocs.io/en/latest/) feature to install Ansible and run `ansible-pull`.

It's a five line shell script:

```shell
#!/bin/bash
yum update -y
yum install epel-release -y
yum install ansible git -y
ansible-pull provision.yml -U ${git_repository} -f --clean --accept-host-key -i localhost, -e git_respository=${git_repository} -e environment=${environment} -e role=${system_role}
```

It includes some variables in here. These variables are managed by [Terraform](https://www.terraform.io) as the script is a Terraform template:

```
data "template_file" "userdata" {
  template = "${file("${path.module}/files/userdata.sh")}"

  vars {
    git_repository = "${var.git_repository}"
    environment = "${var.environment}"
    system_role = "${var.system_role}"
  }
}
```

It's injected via a user data directive within Terraform, which allows for hands off deployments:

```
resource "aws_instance" "bounce" {
  key_name = "Secret Key"
  ami = "ami-fedafc9d"
  instance_type = "t2.nano"
  vpc_security_group_ids = ["${aws_security_group.bounce.id}"]
  subnet_id = "${aws_subnet.bounce.id}"
  user_data = "${data.template_file.userdata.rendered}"
  tags {
    Name = "bouncy-castle"
  }
}
```

The sample here demonstrates a static instance being setup, but the process is exactly same for AWS Launch Configurations (to back an Auto Scaling Group) for dynamically scaling, volatile instances.

Once a system is starting up and this whole process is put into action, two Playbooks then control the present and future state of the new system: `provision.yaml` and `update.yaml`.

## Push, pull, pull later (PPPL)
The provisioning process, the first use of Ansible on the system, is about getting the new system setup and configured to fulfill its role within the network. This is done by executing the correct Ansible Roles against the system and getting the correct state in place. Once complete, there may be a need to quickly and easily update the system later on.

This is why we need a second Playbook - I want to be able to update certain Roles and Playbooks and have them executed across the network, on the right systems, a few minutes later. Or put another way: it's OK to update (static) systems in place.

### The PL in PPPL
The pull later (PL) aspect of this solution can be seen as somewhat of a fail safe, a back door, or simply me covering my arse. Or perhaps the process of building and configuring, only to rebuild and reconfigure again very soon after gets tiresome quickly, especially when the new state is a simple change. But in all honesty, I implemented this part of the solution as a way of controlling access to the system via user accounts and SSH keys. **It's a completely optional part and boisl down to personal preference.**

The second Playbook can be used for a very simple changes which are not only propagated to new systems when they're built in the future, but also to existing systems in the here and now.

## Immutability
I'm a big fan of the immutable (read-only file system) design philosophy when it comes to system engineering and continuous delivery, but it's not realistic for all situations or architectures. That means we still need a solution for updating static infrastructure and a second `ansible-pull` operation is ideal for this.

With a "Push, pull, pull later" (PPPL) model, a simple cronjob and a second Playbook introduces a way of executing one off changes to state across a wide range of systems and frankly, sometimes you just have to get things done in here and now.