

def test_register():
    import datalad.api as da
    assert hasattr(da, 'xnat_init')
