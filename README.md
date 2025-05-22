python-developer-test
Zego
About Us

At Zego, we understand that traditional motor insurance holds good drivers back. It's too complicated, too expensive, and it doesn't reflect how well you actually drive. Since 2016, we have been on a mission to change that by offering the lowest priced insurance for good drivers.

From van drivers and gig economy workers to everyday car drivers, our customers are the driving force behind everything we do. We've sold tens of millions of policies and raised over $200 million in funding. And we’re only just getting started.
Our Values

Zego is thoroughly committed to our values, which are the essence of our culture. Our values defined everything we do and how we do it. They are the foundation of our company and the guiding principles for our employees. Our values are:
Blaze a trail	Blaze a trail	Emphasize curiosity and creativity to disrupt the industry through experimentation and evolution.
Drive to win	Drive to win	Strive for excellence by working smart, maintaining well-being, and fostering a safe, productive environment.
Take the wheel	Take the wheel	Encourage ownership and trust, empowering individuals to fulfil commitments and prioritize customers.
Zego before ego	Zego before ego	Promote unity by working as one team, celebrating diversity, and appreciating each individual's uniqueness.
The Engineering Team

Zego puts technology first in its mission to define the future of the insurance industry. By focusing on our customers' needs we're building the flexible and sustainable insurance products and services that they deserve. And we do that by empowering a diverse, resourceful, and creative team of engineers that thrive on challenge and innovation.
How We Work

    Collaboration & Knowledge Sharing - Engineers at Zego work closely with cross-functional teams to gather requirements, deliver well-structured solutions, and contribute to code reviews to ensure high-quality output.
    Problem Solving & Innovation - We encourage analytical thinking and a proactive approach to tackling complex problems. Engineers are expected to contribute to discussions around optimization, scalability, and performance.
    Continuous Learning & Growth - At Zego, we provide engineers with abundant opportunities to learn, experiment and advance. We positively encourage the use of AI in our solutions as well as harnessing AI-powered tools to automate workflows, boost productivity and accelerate innovation. You'll have our full support to refine your skills, stay ahead of best practices and explore the latest technologies that drive our products and services forward.
    Ownership & Accountability - Our team members take ownership of their work, ensuring that solutions are reliable, scalable, and aligned with business needs. We trust our engineers to take initiative and drive meaningful progress.

Who should be taking this test?

This test has been created for all levels of developer, Junior through to Staff Engineer and everyone in between. Ideally you have hands-on experience developing Python solutions using Object Oriented Programming methodologies in a commercial setting. You have good problem-solving abilities, a passion for writing clean and generally produce efficient, maintainable scaleable code.
The test 🧪

Create a Python app that can be run from the command line that will accept a base URL to crawl the site. For each page it finds, the script will print the URL of the page and all the URLs it finds on that page. The crawler will only process that single domain and not crawl URLs pointing to other domains or subdomains. Please employ patterns that will allow your crawler to run as quickly as possible, making full use any patterns that might boost the speed of the task, whilst not sacrificing accuracy and compute resources. Do not use tools like Scrapy or Playwright. You may use libraries for other purposes such as making HTTP requests, parsing HTML and other similar tasks.
The objective

This exercise is intended to allow you to demonstrate how you design software and write good quality code. We will look at how you have structured your code and how you test it. We want to understand how you have gone about solving this problem, what tools you used to become familiar with the subject matter and what tools you used to produce the code and verify your work. Please include detailed information about your IDE, the use of any interactive AI (such as Copilot) as well as any other AI tools that form part of your workflow.

You might also consider how you would extend your code to handle more complex scenarios, such a crawling multiple domains at once, thinking about how a command line interface might not be best suited for this purpose and what alternatives might be more suitable. Also, feel free to set the repo up as you would a production project.

Extend this README to include a detailed discussion about your design decisions, the options you considered and the trade-offs you made during the development process, and aspects you might have addressed or refined if not constrained by time.
Instructions

    Create a repo.
    Tackle the test.
    Push the code back.
    Add us (@2014klee, @danyal-zego, @bogdangoie and @cypherlou) as collaborators and tag us to review.
    Notify your TA so they can chase the reviewers.


---- 

Installed expected core libraries for web crawling.
created application directory to store core app logic.
Installed black and pylint for code formatting and linting.
Started the WebCrawler class to handle the crawling logic, created with a single url currently.
requirements.txt updated.
Makefile added to run common tasks quickly.
Use co-pilot to help with docstrings and basic exception handling.
next: research online and implement a simple command line interface to run the crawler.
click library installed for the CLI interaction, chosen as its part of Python's standard library and is well documented, reducing the need for extra dependencies.
Added a simple command line interface to the WebCrawler class, allowing users to input a URL and start the crawling process, with some fallback and help options.
Added a file manager class so users can save the results of the domain crawling to a file locally, in a few common formats, basic.
Include the pylintrc file to exclude common false positives in my opinion.

next, investigate the current functionality vs the actual requirements of the project, ensure we achieve the desired results.
also, think about how to enhance functionality with tools like aiohttp that can handle large crawls, another impact is how filemanager will handle large amount of urls to save to a local file, needs to be scalable and efficient.
