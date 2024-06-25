write_mdb.py
============

If a system is marked as *writable* in the loader tree, Yamcs becomes responsible for updating the file, and the HTTP API can then be used to update it. This capability exists only for XTCE files.

Note that this functionality is experimental, and does not offer the same degree of customizations as when loading the MDB from a predefined XTCE file.

To demonstrate this capability, add a writable subsystem ``test`` to the `Yamcs Quickstart <https://github.com/yamcs/quickstart/>`_ example:

.. code-block:: yaml
    :caption: :file:`mdb/yamcs.myproject.yaml`

    mdb:
      - type: xtce
        args:
          file: mdb/xtce.xml
        subLoaders:
          - type: xtce
            writable: true
            args:
              file: /path/to/test.xml

Because the quickstart example works on a copy of the files (in :file:`target/yamcs/`), we specify :file:`test.xml` as an absolute rather than relative reference.

The initial content can just be an empty XTCE SpaceSystem, specifying its name:

.. code-block:: xml
    :caption: :file:`mdb/test.xml`

    <?xml version="1.0" encoding="UTF-8"?>
    <SpaceSystem xmlns="http://www.omg.org/spec/XTCE/20180204" name="test">
    </SpaceSystem>

Then you can add parameter types and values like this:

.. literalinclude:: ../../yamcs-client/examples/write_mdb.py

Afterwards you should see that :file:`test.xml` has been updated automatically:

.. code-block:: xml
    :caption: :file:`mdb/test.xml`

    <?xml version="1.0" encoding="UTF-8"?>
    <SpaceSystem xmlns="http://www.omg.org/spec/XTCE/20180204" name="test">
      <TelemetryMetaData>
        <ParameterTypeSet>
          <FloatParameterType sizeInBits="32" name="float_t">
            <UnitSet/>
          </FloatParameterType>
        </ParameterTypeSet>
        <ParameterSet>
          <Parameter parameterTypeRef="float_t" name="testparam">
            <ParameterProperties dataSource="local" persistence="false"/>
          </Parameter>
        </ParameterSet>
      </TelemetryMetaData>
    </SpaceSystem>
