"""
Fuzzy Logic Controller for Traffic Light Optimization
"""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt
from typing import Tuple


class TrafficLightController:
    """Fuzzy logic controller for adaptive traffic light timing"""
    
    MIN_GREEN_TIME = 15
    MAX_GREEN_TIME = 60
    
    def __init__(self, light_id: str):
        self.light_id = light_id
        self._setup_fuzzy_system()
    
    def _setup_fuzzy_system(self):
        """Initialize fuzzy logic system with membership functions and rules"""
        # Define universe variables
        self.density = ctrl.Antecedent(np.arange(0, 101, 1), 'density')
        self.wait = ctrl.Antecedent(np.arange(0, 121, 1), 'wait')
        self.green = ctrl.Consequent(np.arange(5, 91, 1), 'green')
        self.green.defuzzify_method = 'centroid'
        
        # Define membership functions
        self._define_membership_functions()
        
        # Define fuzzy rules
        rules = self._create_fuzzy_rules()
        
        # Create control system
        self.control_system = ctrl.ControlSystem(rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def _define_membership_functions(self):
        """Define membership functions for inputs and output"""
        # Density membership functions
        self.density['low'] = fuzz.trapmf(self.density.universe, [0, 0, 25, 45])
        self.density['medium'] = fuzz.trimf(self.density.universe, [25, 50, 75])
        self.density['high'] = fuzz.trapmf(self.density.universe, [55, 75, 100, 100])
        
        # Wait time membership functions
        self.wait['short'] = fuzz.trapmf(self.wait.universe, [0, 0, 30, 50])
        self.wait['medium'] = fuzz.trimf(self.wait.universe, [30, 60, 90])
        self.wait['long'] = fuzz.trapmf(self.wait.universe, [70, 90, 120, 120])
        
        # Green time membership functions
        self.green['short'] = fuzz.trapmf(self.green.universe, [5, 5, 20, 35])
        self.green['medium'] = fuzz.trimf(self.green.universe, [20, 40, 60])
        self.green['long'] = fuzz.trapmf(self.green.universe, [45, 60, 90, 90])
    
    def _create_fuzzy_rules(self):
        """Create comprehensive fuzzy rule base"""
        return [
            # Low density rules
            ctrl.Rule(self.density['low'] & self.wait['short'], self.green['short']),
            ctrl.Rule(self.density['low'] & self.wait['medium'], self.green['medium']),
            ctrl.Rule(self.density['low'] & self.wait['long'], self.green['medium']),
            
            # Medium density rules
            ctrl.Rule(self.density['medium'] & self.wait['short'], self.green['medium']),
            ctrl.Rule(self.density['medium'] & self.wait['medium'], self.green['medium']),
            ctrl.Rule(self.density['medium'] & self.wait['long'], self.green['long']),
            
            # High density rules
            ctrl.Rule(self.density['high'] & self.wait['short'], self.green['long']),
            ctrl.Rule(self.density['high'] & self.wait['medium'], self.green['long']),
            ctrl.Rule(self.density['high'] & self.wait['long'], self.green['long']),
        ]
    
    def compute_green_time(self, density: float, wait_time: float) -> float:
        """
        Compute optimal green light duration using fuzzy logic
        
        Args:
            density: Traffic density (0-100)
            wait_time: Average waiting time in seconds (0-120)
        
        Returns:
            Optimal green light duration in seconds
        """
        try:
            # Clamp inputs to valid ranges
            density = np.clip(density, 0, 100)
            wait_time = np.clip(wait_time, 0, 120)
            
            # Compute fuzzy inference
            self.simulator.input['density'] = density
            self.simulator.input['wait'] = wait_time
            self.simulator.compute()
            
            # Get and clamp output
            raw_output = self.simulator.output['green']
            clamped_output = np.clip(raw_output, self.MIN_GREEN_TIME, self.MAX_GREEN_TIME)
            
            return round(clamped_output, 1)
            
        except Exception as e:
            print(f"Fuzzy computation error for {self.light_id}: {e}")
            return 30.0  # Safe fallback value
    
    def visualize_membership_functions(self, save_path: str = None):
        """
        Visualize membership functions for inputs and output
        
        Args:
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(3, 1, figsize=(10, 8))
        
        # Density membership functions
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['low'].mf, self.density.universe), 'b', label='Low')
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['medium'].mf, self.density.universe), 'g', label='Medium')
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['high'].mf, self.density.universe), 'r', label='High')
        axes[0].set_title('Traffic Density Membership Functions', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Density (%)')
        axes[0].set_ylabel('Membership')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Wait time membership functions
        
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['short'].mf, self.wait.universe), 'b', label='Short')
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['medium'].mf, self.wait.universe), 'g', label='Medium')
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['long'].mf, self.wait.universe), 'r', label='Long')
        axes[1].set_title('Wait Time Membership Functions', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Wait Time (seconds)')
        axes[1].set_ylabel('Membership')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        
        # Green time membership functions
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['short'].mf, self.green.universe), 'b', label='Short')
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['medium'].mf, self.green.universe), 'g', label='Medium')
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['long'].mf, self.green.universe), 'r', label='Long')
        axes[2].set_title('Green Light Duration Membership Functions', fontsize=12, fontweight='bold')
        axes[2].set_xlabel('Green Time (seconds)')
        axes[2].set_ylabel('Membership')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def visualize_inference(self, density: float, wait_time: float, save_path: str = None):
        """
        Visualize the fuzzy inference process for given inputs
        
        Args:
            density: Traffic density (0-100)
            wait_time: Average waiting time in seconds (0-120)
            save_path: Optional path to save the figure
        """
        # Clamp inputs
        density = np.clip(density, 0, 100)
        wait_time = np.clip(wait_time, 0, 120)
        
        # Compute output
        green_time = self.compute_green_time(density, wait_time)
        
        # Calculate membership degrees
        density_low = fuzz.interp_membership(self.density.universe, self.density['low'].mf, density)
        density_medium = fuzz.interp_membership(self.density.universe, self.density['medium'].mf, density)
        density_high = fuzz.interp_membership(self.density.universe, self.density['high'].mf, density)
        
        wait_short = fuzz.interp_membership(self.wait.universe, self.wait['short'].mf, wait_time)
        wait_medium = fuzz.interp_membership(self.wait.universe, self.wait['medium'].mf, wait_time)
        wait_long = fuzz.interp_membership(self.wait.universe, self.wait['long'].mf, wait_time)
        
        # Create visualization
        fig, axes = plt.subplots(3, 1, figsize=(12, 18))
        
        # Plot density with current value
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['low'].mf, self.density.universe), 'b', linewidth=2, label='Low')
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['medium'].mf, self.density.universe), 'g', linewidth=2, label='Medium')
        axes[0].plot(self.density.universe, fuzz.interp_membership(self.density.universe, self.density['high'].mf, self.density.universe), 'r', linewidth=2, label='High')
        axes[0].axvline(density, color='black', linestyle='--', linewidth=2, label=f'Input: {density:.1f}%')
        axes[0].set_title(f'Density Fuzzification (Low: {density_low:.2f}, Medium: {density_medium:.2f}, High: {density_high:.2f})', 
                         fontsize=9, fontweight='bold')
        axes[0].set_xlabel('Density (%)')
        axes[0].set_ylabel('Membership')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot wait time with current value
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['short'].mf, self.wait.universe), 'b', linewidth=2, label='Short')
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['medium'].mf, self.wait.universe), 'g', linewidth=2, label='Medium')
        axes[1].plot(self.wait.universe, fuzz.interp_membership(self.wait.universe, self.wait['long'].mf, self.wait.universe), 'r', linewidth=2, label='Long')
        axes[1].axvline(wait_time, color='black', linestyle='--', linewidth=2, label=f'Input: {wait_time:.1f}s')
        axes[1].set_title(f'Wait Time Fuzzification (Short: {wait_short:.2f}, Medium: {wait_medium:.2f}, Long: {wait_long:.2f})', 
                         fontsize=9, fontweight='bold')
        axes[1].set_xlabel('Wait Time (seconds)')
        axes[1].set_ylabel('Membership')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Plot output with defuzzified value
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['short'].mf, self.green.universe), 'b', linewidth=2, label='Short')
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['medium'].mf, self.green.universe), 'g', linewidth=2, label='Medium')
        axes[2].plot(self.green.universe, fuzz.interp_membership(self.green.universe, self.green['long'].mf, self.green.universe), 'r', linewidth=2, label='Long')
        axes[2].axvline(green_time, color='black', linestyle='--', linewidth=3, label=f'Output: {green_time:.1f}s')
        axes[2].fill_between(self.green.universe, 0, 
                            fuzz.interp_membership(self.green.universe, self.green.output_mf, self.green.universe),
                            alpha=0.3, color='orange', label='Aggregated Output')
        axes[2].set_title(f'Defuzzification → Green Time: {green_time:.1f} seconds', 
                         fontsize=9, fontweight='bold')
        axes[2].set_xlabel('Green Time (seconds)')
        axes[2].set_ylabel('Membership')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()


if __name__ == "__main__":
    # Demo: Visualize membership functions and inference
    controller = TrafficLightController("demo")
    
    print("Generating membership function visualization...")
    controller.visualize_membership_functions()
    
    print("\nTesting inference with different scenarios:")
    test_cases = [
        (20, 25, "Low density, short wait"),
        (50, 60, "Medium density, medium wait"),
        (85, 95, "High density, long wait"),
    ]
    
    for density, wait, description in test_cases:
        green_time = controller.compute_green_time(density, wait)
        print(f"{description}: Density={density}%, Wait={wait}s → Green={green_time}s")
        controller.visualize_inference(density, wait)
