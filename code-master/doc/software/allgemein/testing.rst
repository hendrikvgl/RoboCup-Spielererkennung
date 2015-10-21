Testing
^^^^^^^

.. todo:: Amtsprache Deutsch

In general the testing of source code is not only necessary to exclude bugs 
but also to be resistent when you refactor existing code fragments.


Unit-Tests
----------

Unittests are the smallest and fastes test that are available. They should be used 
whenever you want to test the basic functions of you single methods. For future
code or legacy code you are working on please write unittests if there aren't any.

Sample::

    import unittest
    
    class TestFeature(object):
        
        def setUp(self):
            """ This is called each time before every test method runs """
            self.feature = Feature()
        
        def test_feature_calculates_correctly(self):
            #Prepare the data
            data = {"BallFound" : True, "Penalty" : False}
            # Call the feature
            action = self.feature.determine_action(data)
            # Check the result
            self.assertEquals("GoToBall", action)
            
The unittests for every python class, if available, are located in a folder named *tests* within the directory the python file is located.

* tests/

  * testFeatureA.py
  * testFeatureB.py
* FeatureA.py
* FeatureB.py
* FeatureC.py


Quality - Checks
----------------

There are software parts within the project that are extremly hard to test for correct behaviour.
One example could be the vision which relies on real data to be evaluated.

Nevertheless if you are working on such a *nondeterministic* theme make sure you have some form of automated
evaluation so that you can make modification to the underling software but test it again with the same input.
This is necessary to see if you made changes that go toally in the wrong direction.
