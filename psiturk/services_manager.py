from psiturk.amt_services_wrapper import MTurkServicesWrapper

class PsiturkServicesManager():
    _cached_amt_services_wrapper = None
    
    @property 
    def amt_services_wrapper(self):
        if not self._cached_amt_services_wrapper:
            self._cached_amt_services_wrapper = MTurkServicesWrapper()
        return self._cached_amt_services_wrapper
        
psiturk_services_manager = PsiturkServicesManager()