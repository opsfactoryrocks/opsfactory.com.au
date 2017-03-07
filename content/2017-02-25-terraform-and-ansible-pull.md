Title: Terraform and Ansible Pull
Date: 2017-03-05
Category: Automation
Tags: ansible, confmg, terraform, infrastructure
Slug: terraform-and-ansible-pull
Authors: Michael Crilly
Summary: Pulling instead of pushing for self-provisioning systems is very powerful, especially without a centralised authority to maintain.

I was first introduced to Configuration Management via [Puppet](https://puppet.com/product). I used it extensively at several engagements and it did the job rather well. The DSL was workable, writing modules was simple enough, and Puppet its self, as well as the projects around it ([Foreman](https://www.theforeman.org) and [Hiera](https://docs.puppet.com/hiera/)) did a great job of making the whole state management process easier.

During that time I had also discovered and grew very fond of Ansible. It was quickly becoming the superior product from my perspective, primarily due to the simple integration and push (by default) based model. **I haven't touched Puppet for nearly four years.**

Although Ansible won out with its push model, time and time again I found managing inventories and executing tasks locally tedious. I often caught my self wishing I could actually just implement some centralised system that Ansible pulled from. I obviously knew of `ansible-pull`, but what would the architecture look like? How could I still get Ansible's frictionless push model integration into a network and still remove the need for dealing with inventories?

I essentially wanted to update the state, push it, and then have the network apply the new state.

## A shell script
After thinking about various solutions, which obviously involved a lot of overthinking, I eventually settled on an extremely obvious, very simple but effective solution: a shell script executed on a new instance via the user data/[cloud-init](https://cloudinit.readthedocs.io/en/latest/) feature to install Ansible and run `ansible-pull`.

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

The sample here demonstrates a static instance being setup, but the process is exactly the same for AWS Launch Configurations (to back an Auto Scaling Group) for dynamically scaling, volatile instances.

Once a system is starting up and this whole process is put into action, two Playbooks then control the present and future state of the new system: `provision.yaml` and `update.yaml`.

### Provisioning
The process of provisioning the system is the first stage to the management of the OS and above. This stage gets the system ready to perform its role and in a stable condition.

### Updating
The process of updating the system in place is somewhat optional in this architecture. Some people don't like the idea of updating infrastructure in place, especially now with the ease of implementing CI/CD processes; automation tools; testing; and so on. Feel free to omit this option.

## That's the basics
With the right amount of consideration, the `ansible-pull` model of working is rather quite simple, easy to grasp and implement, and uses tools already present in the network (most likely, anyway.)

Like all solutions, however, it can't be everything to everyone.