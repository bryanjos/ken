DROP INDEX source_id_idx;
CREATE UNIQUE INDEX source_id_idx ON information (source, source_id);

Create Function ignore_info_dups() Returns Trigger
As $$
Begin
    If Exists (
        Select
            source, source_id
        From
            information i
        Where
            i.source = NEW.source
            And i.source_id = NEW.source_id
    ) Then
        Return NULL;
    End If;
    Return NEW;
End;
$$ Language plpgsql;

Create Trigger ignore_info_dups
    Before Insert On information
    For Each Row
    Execute Procedure ignore_info_dups();