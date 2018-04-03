Using external survey tools with **psiTurk**
=============================================

With the magic of ``iframes`` and javascript window messaging, you can integrate
external survey tools into your **psiTurk** experiment. This is possible as long as the survey tool
allows custom javascript to be triggered.

Window messaging allows cross-domain messaging via javascript, without having to configure security settings on the server. `MDN`_ says it best:

    "The ``window.postMessage`` method safely enables cross-origin communication. Normally, scripts on different pages are allowed to access each other if and only if the pages that executed them are at locations with the same protocol (usually both ``https``), port number (443 being the default for ``https``), and host (modulo ``document.domain`` being set by both pages to the same value). ``window.postMessage`` provides a controlled mechanism to circumvent this restriction in a way which is secure when properly used."

.. _MDN: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage

Three special steps to hook up your survey to **psiTurk**:

1. Embed your survey as an ``iframe`` within one of your **psiTurk** pages or views.
2. Add a ``message`` event listener to your **psiTurk** window
3. Post a ``message`` from the survey tool to the ``window.top`` when the survey is complete. ``window.top`` will be your **psiTurk** window. Do whatever you want via javascript once you receive the expected ``message``.

To tie the **psiTurk** data and the external survey data together, embed a unique id into the iframe url you load, and then record that unique url into your survey data. *Don't forget to do this. If you forget, you won't know to who to connect your survey data.* If you want to tie things both ways, post back your survey session id as part of the survey-complete post-back.


An example with Qualtrics
~~~~~~~~~~~~~~~~~~~~~~~~~

As of the time this documentation page was written, Qualtrics has an undocumented "feature". Qualtrics automatically posts a window ``message`` to ``window.top`` when the Qualtrics "end of the survey event" is triggered. For Qualtrics surveys embedded as ``iframes`` in **psiTurk** experiments, we can take advantage of this behavior. The Qualtrics-posted message contains your ``survey_id`` and the participant's Qualtrics-created unique ``session_id``. You should already know the ``survey_id`` (because you just embedded a link containing this id), but the ``session_id`` is Qualtric's unique id for whoever just finished your survey. You can record that with **psiTurk** as unstructured data (see :ref:`recording-unstructured-data-label`) if you desire.

*Don't forget to explicitly log the psiTurk unique id as embedded data within Qualtrics.* See `here`__ for more about embedding data into Qualtrics surveys.

.. _qualtrics-embedded-data: https://www.qualtrics.com/university/researchsuite/advanced-building/survey-flow/embedded-data/
__ qualtrics-embedded-data_

The posted message when they finish a qualtrics survey is a string that looks like this::

    QualtricsEOS|<survey_id>|<qualtrics_session_id>

So you can do something like this on your **psiTurk** page:

.. code-block:: javascript

    // load your iframe with a url specific to your participant
    $('#iframe').attr('src','<your qualtrics url>&UID=' + uniqueId);

    // add the all-important message event listener
    window.addEventListener('message', function(event){

        // normally there would be a security check here on event.origin (see the MDN link above), but meh.
        if (event.data) {
            if (typeof event.data === 'string') {
                q_message_array = event.data.split('|');
                if (q_message_array[0] == 'QualtricsEOS') {
                    psiTurk.recordTrialData({'phase':'postquestionnaire', 'status':'back_from_qualtrics'});
                    psiTurk.recordUnstructuredData('qualtrics_session_id', q_message_array[2]);
                }
            }
        }
        // display the 'continue' button, which takes them to the next page
        $('#next').show();
    })

This code can be put on a page that has a link with ``id #next`` default-hidden via css which advances the participant to the next experimental page. Note that this code checks that the event is ``QualtricsEOS`` before continuing on. That's because Qualtrics posts other events to ``window.top``, too. This code is only interested in the EndOfSurvey event.

Also notice that this code doesn't implement any security precautions. `Normally it's good practice to check to see where a message is coming from before you act on it`__. For instance, it might check to verify that the message is coming from a qualtrics.com domain. But in this code, the worst-case scenario is that a tech-savvy participant somehow triggers that they completed the survey before they actually did. In that case, their survey data would be blank, and after visual inspection their assignment could be rejected.

.. _security_concerns: https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage#Security_concerns
__ security_concerns_


What about not-Qualtrics?
~~~~~~~~~~~~~~~~~~~~~~~~~

If your survey tool isn't posting messages to window.top for you, just ``window.top.postMessage(<message>, <targetOrigin>)`` yourself. For instance, you might have javascript in your survey tool that does:

.. code:: javascript

    window.top.postMessage("all_done|<survey_session_id>","*")

Then just listen for that event back on your **psiTurk** page, as in the Qualtrics example above.
