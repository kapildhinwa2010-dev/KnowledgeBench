import pytest
import torch
from knowledgebench import KnowledgeBench, create_knowledgebench

class TestKnowledgeBench:
    def test_init(self):
        m = KnowledgeBench(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = KnowledgeBench(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_knowledgebench()
        assert isinstance(m, KnowledgeBench)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
