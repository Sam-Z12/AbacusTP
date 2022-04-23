# Run All Tests

#### From Abacus dir run cmd

    pyest

#### Run with verbose and allow printing

    pytest -v -s

#### Run a specific file or dir

    pytest tests/filename

#### Run only one test function

    pytest tests/file_name::function_name


# Test Database
#### First Create All Tables With

    Base.metadata.create_all(bind=engine)

#### Last Drop All Tables

    Base.metadata.create_all(bind=engine)

#### Can Override Dependency Args With

    app.dependency_overrides[func_name] = override_func_name