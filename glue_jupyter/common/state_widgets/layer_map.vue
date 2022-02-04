<template>
    <div>
        <div>
            <v-select :items="c_att_items" label="choropleth" v-model="c_att_selected"/>
        </div>
    </div>
</template>
<script>
    module.exports = {
    }
</script>
<style>
    .v-navigation-drawer {
    z-index: 999999 !important;
    }
</style>