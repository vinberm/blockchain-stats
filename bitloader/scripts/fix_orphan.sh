#!/bin/bash

ROOT_DIR='/home/admin'
LOG_FILE='nohup.out'

cd $ROOT_DIR
for id in $(cat $LOG_FILE | grep disconnect |awk '{print $2}')
do
        echo $id
        mysql -N -e "use bitcoin; select DISTINCT pubkey_id from txout_detail where pubkey_id is not NULL and block_id=$id" >> pk_tmp
        mysql -N -e "use bitcoin; select DISTINCT pubkey_id from txin_detail where pubkey_id is not NULL and block_id=$id" >> pk_tmp

        (( next_id=$id+1 ))
        echo $next_id

        mysql -N -e "use bitcoin; select DISTINCT pubkey_id from txout_detail where pubkey_id is not NULL and block_id=$next_id" >> orphan_pks
        mysql -N -e "use bitcoin; select DISTINCT pubkey_id from txin_detail where pubkey_id is not NULL and block_id=$next_id" >> orphan_pks

done

cat pk_tmp |sort |uniq > orphans
rm -rf orphan_pks
split -l 2000 orphans orph_