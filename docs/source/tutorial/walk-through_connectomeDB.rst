.. _walktrhough:

Walk-trhough connectomeDB
=========================

This walk-through tutorial shows how to obtain the subjects in a project of the ConnecotmeDB
It is assumed that you have a working installatin of datalad-xant and you have accepted the data usaer agreement in connectomeDB.

Create a Datalad dataset. Here we'll call the dataset *hcp*

``datalad create hcp``

Move into the *hcp* dataset.

``cd hcp``

Initialize XNAT to track ConnectomeDB, and list all the projects in ConnectomeDB.We will use the project *WU_L1A_Subj*.

``datalad xnat-init https://db.humanconnectome.org``


``datalad xnat-init https://db.humanconnectome.org --project WU_L1A_Subj``

If a dataset was already initialized before, you will need to forze the initialization.

``datalad xnat-init https://db.humanconnectome.org --project MGH_DIFF --force``

List all subjects within the project.

``datalad xnat-update``

Download all data that belongs to a subject, here subject ConnectomeDB_S01439. Make sure that you have enough free space on your disk.

``datalad xnat-update -s ConnectomeDB_S01439``

Now the data should start to download. 
