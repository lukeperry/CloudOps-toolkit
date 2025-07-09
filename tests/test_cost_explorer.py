import sys
import os
import unittest.mock as mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.cost_explorer import get_cost_summary, get_cost_by_service, get_daily_costs


class TestCostExplorer:
    """Test cases for AWS Cost Explorer functions"""
    
    @mock.patch('app.cost_explorer.get_boto3_client')
    def test_get_cost_summary_success(self, mock_client):
        """Test successful cost summary retrieval"""
        mock_ce = mock.MagicMock()
        mock_client.return_value = mock_ce
        
        mock_ce.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'Total': {
                        'UnblendedCost': {
                            'Amount': '123.45'
                        }
                    }
                }
            ]
        }
        
        result = get_cost_summary()
        
        assert result['Cost (USD)'] == 123.45
        assert 'Month' in result
        assert 'Period' in result
    
    @mock.patch('app.cost_explorer.get_boto3_client')
    def test_get_cost_summary_error(self, mock_client):
        """Test cost summary with error"""
        mock_client.side_effect = Exception("Cost Explorer access denied")
        
        result = get_cost_summary()
        
        assert "Error" in result
        assert "Cost Explorer access denied" in result["Error"]
    
    @mock.patch('app.cost_explorer.get_boto3_client')
    def test_get_cost_by_service_success(self, mock_client):
        """Test successful cost by service retrieval"""
        mock_ce = mock.MagicMock()
        mock_client.return_value = mock_ce
        
        mock_ce.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'Groups': [
                        {
                            'Keys': ['Amazon Elastic Compute Cloud - Compute'],
                            'Metrics': {
                                'UnblendedCost': {
                                    'Amount': '50.00'
                                }
                            }
                        },
                        {
                            'Keys': ['Amazon Simple Storage Service'],
                            'Metrics': {
                                'UnblendedCost': {
                                    'Amount': '25.00'
                                }
                            }
                        }
                    ]
                }
            ]
        }
        
        result = get_cost_by_service()
        
        assert len(result) == 2
        assert result[0]['Service'] == 'Amazon Elastic Compute Cloud - Compute'
        assert result[0]['Cost (USD)'] == 50.00
        assert result[1]['Service'] == 'Amazon Simple Storage Service'
        assert result[1]['Cost (USD)'] == 25.00
    
    @mock.patch('app.cost_explorer.get_boto3_client')
    def test_get_daily_costs_success(self, mock_client):
        """Test successful daily costs retrieval"""
        mock_ce = mock.MagicMock()
        mock_client.return_value = mock_ce
        
        mock_ce.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'TimePeriod': {'Start': '2023-01-01'},
                    'Total': {
                        'UnblendedCost': {
                            'Amount': '10.00'
                        }
                    }
                },
                {
                    'TimePeriod': {'Start': '2023-01-02'},
                    'Total': {
                        'UnblendedCost': {
                            'Amount': '12.00'
                        }
                    }
                }
            ]
        }
        
        result = get_daily_costs(30)
        
        assert len(result) == 2
        assert result[0]['Date'] == '2023-01-01'
        assert result[0]['Cost (USD)'] == 10.00
        assert result[1]['Date'] == '2023-01-02'
        assert result[1]['Cost (USD)'] == 12.00
