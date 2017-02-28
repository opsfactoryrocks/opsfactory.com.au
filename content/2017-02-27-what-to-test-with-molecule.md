Title: Only test the end result
Date: 2017-02-27
Category: Testing
Tags: molecule, testing
Slug: only-test-the-end-result
Authors: Michael Crilly
Summary: Don't test every unit or funtion, just test the end the result.

It was only yesterday that I wrote about [Testing Ansible Roles with Molecule]({filename}2017-02-25-testing-ansible-roles-with-molecule.md), and today I wanted to write a short explanation of what I believe is the correct use case for testing Ansible Roles.

Testing is an important part of software engineering and development. It provides several advantages and has been widely accepted as a successful paradigm. Some pretty [key](http://david.heinemeierhansson.com/2014/tdd-is-dead-long-live-testing.html) [players](http://rbcs-us.com/documents/Why-Most-Unit-Testing-is-Waste.pdf) in the industry, however, have pointed out the importance of balance and ensuring that a suite of tests is carefully implemented and curated throughout their life (which is finite.) I agree.

With Ansible Roles, I believe the same is true: think abount what actually needs to be tested and test it, but make sure the tests you've written are still relevant when you revisit them further down the line.

## Linting
The fantastic `ansible-lint` by [Will Thames](http://willthames.github.io) (who I've had the pleasure of working with) is a great start to ensuring your YAML/Ansible falls in line with common best practices. 

This is a no brainer, really. By following best development practices, like making sure you name tasks; and having service restart tasks moved into handlers, are all perfectly valid and correct things to be checking for.

## Flake8
If you're writing custom Python modules, or have any Python littered throughout your repository at all, then [flake8](http://flake8.pycqa.org/en/latest/), like `ansible-lint`, ensures best practices are being adhered to. 

I don't believe there's possibly a counter argument here.

## Testinfra
So here's where it gets interesting. A good friend of mine, [James Belchamber](http://james.belchamber.com), commented on that article explaining how he feels it's not constructive to test every unit, which in the case of an Ansible Playbook or Role, is probably the result of every module call (`user`, `file`, `template`, `ec2_instance`, etc.) I agree with this view of testing Roles and Playbooks, and so I wanted to clarify what I would want to see tested in a well maintained, tested Role: **the final result**

The final result is the intended outcome of the Role or Playbook, which could be, but certaintly isn't limited to:

- The service or software being managed
- A particular file or set of that should have been created
- A set of users that should now exist
- The correct SSL certificates were put in place
- That NFS mount that's needed by another process (managed by another Role)

And so on.

If your Role introduces a new service to the network, test that it came up, but don't test Ansible correctly uploaded every file involved, created the service's user, or correctly set the hostname. If the services doesn't come up, **use the Ansible output as a log to determine why.** Once you've fixed the issue, the service comes up and your Testinfra tests pass.

Use Ansible's output log as an audit trail for when things fail, but until that happens, just test the final results are what you expected and move on.