```eval_rst
.. toctree::
   :caption: First Steps
   :maxdepth: 2
   :hidden:

   what_is_psiturk
   getting_started
   collecting_data
   anatomy_of_project   
   dashboard

.. toctree::
  :caption: Topic Guides
  :maxdepth: 2
  :hidden:

  topic_guides/install
  topic_guides/recording
  topic_guides/retrieving
  topic_guides/amt_setup
  topic_guides/customizing
  topic_guides/command_line_overview
  topic_guides/alternative_recruitment_channels

.. toctree::
  :caption: Tutorials
  :maxdepth: 2
  :hidden:

  tutorials/heroku
  tutorials/example-project-stroop
  tutorials/using-jspsych
  tutorials/static-ip-ssl
  tutorials/external_surveys
  tutorials/auto-bonus
  tutorials/cookbook

.. toctree::
  :caption: Reference Guides
  :maxdepth: 2
  :hidden:

  reference/api
  reference/settings
  reference/command_line
  reference/migrating

.. toctree::
  :caption: Support
  :maxdepth: 2
  :hidden:

  support/disclaimer
  support/getting_help
  support/code_of_conduct
  Discussion forum <https://groups.google.com/forum/#!forum/psiturk>
  support/roadmap
  support/contribute
  Source code & issue tracker <https://github.com/nyuccl/psiturk/>
```

# Welcome to psiturk

[`psiturk`](https://psiturk.org/) is an open-source Python library that makes it easy to create high-quality behavioral experiments that are delivered over the Internet using a web browser.  

`psiturk` is not, _by itself_, used for creating surveys or interfaces in the browser (for that we recommend tools like [jspych](https://www.jspsych.org) or [d3.js](https://d3js.org)).  Instead, `psiturk` solves the _other_ myriad of problems that come up in web experimentation including:
- Reliably and securely serving webpages to participants over the internet
- Blocking repeat participation (when desired)
- Counterbalancing conditions
- Incrementally saving data to databases
- Simplifying the process of soliciting and approving work on crowdworking sites

`psiturk` is used in [many research fields](https://scholar.google.com/scholar?oi=bibs&hl=en&cites=4685239787075608864) ranging from cognitive science, psychology, neuroscience, bioinformatics, marketing, computer security, user interface testing, computer science, and machine learning in both academia and industry.


## Video introduction

Still unsure if psiturk is for you?  Try this quick five minute video introduction!

---

## How to use our docs

The docs are broken up into several sections:

- **First Steps**: include [What is psiturk?](what_is_psiturk) as an overview.  Then there is a quick-start guide in two main parts: [Getting started developing](getting_started) and [Collecting data](collecting_data).

- **Topic guides**: give you background on specific aspects of `psiturk` including how to [install](topic_guides/install), how to [record](topic_guides/recording) and [retrieve](topic_guides/retrieving) data, how to [set up a Mechanical Turk account](topic_guides/amt_setup), and how to use psiturk with other recruitment systems such as [in the lab](topic_guides/alternative_recruitment_channels).

- **Tutorials**: provides high level overview of specific tasks such as [using psiturk with jsPsych](tutorials/using-jspsych) or [automatically computing performance-based bonus payment amounts](auto-bonus).  Make sure to check out the sections on the [sample project walk-through](example-project-stroop).

- **Reference guides**: are the bread and butter of how our [APIs](reference/api) and [configuration files](reference/configuration-overview) work and will give you short, actionable explanations of specific functions and features.

- **Support**: gives you more options for when you're [stuck](support/getting_help) or want to talk about an idea with other people.

---

## **Open source, community-built**

`psiturk` is built using an open source ([MIT License](https://github.com/NYUCCL/psiTurk/blob/master/LICENSE)) model that draws from the community to share best online experiment practices.  Version 1.0 was launched in November 2013 and since then psiturk has maintained a diverse and supportive community that includes over 40 contributors providing 1800 commits. We happily accept bug reports, feature requests, and -- even better -- pull requests**🎈**! 


## **Join the community**

Please come join us on the [community forum](https://groups.google.com/forum/#!forum/psiturk) or follow us on [twitter](https://twitter.com/psiturk).  We love to hear your questions, ideas, and help you work through your bugs on our github [issues tracker](https://github.com/NYUCCL/psiturk/issues)!  The project leaders are [Dave Eargle](https://daveeargle.com) and [Todd Gureckis](http://gureckislab.org).


   ```eval_rst
   .. note::

      **Citing this project in your papers**:

      To credit `psiturk` in your work, please cite both the original journal paper and a version of the Zenodo archive.  The former provides a high level description of the package, and the latter points to a permanent record of all `psiturk` versions (we encourage you to cite the specific version you used). Example citations (for `psiturk` 3.0.6):

      **Zenodo Archive**:  

      Eargle, David, Gureckis, Todd, Rich, Alexander S., McDonnell, John, & Martin, Jay B. (2021, March 28). 
      psiTurk: An open platform for science on Amazon Mechanical Turk (Version v3.0.6). Zenodo. http://doi.org/10.5281/zenodo.3598652

      **Journal Paper**:  

      Gureckis, T.M., Martin, J., McDonnell, J., Rich, A.S., Markant, D., Coenen, A., Halpern, D., Hamrick, J.B., Chan, P. (2016) psiTurk: An open-source framework for conducting replicable behavioral experiments online. Behavioral Research Methods, 48 (3), 829-842.	DOI: http://doi.org/10.3758/s13428-015-0642-8 
   ```