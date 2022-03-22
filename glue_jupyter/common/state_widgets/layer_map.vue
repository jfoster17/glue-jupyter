<template>
    <div>
        <div>
            <v-select :items="color_att_items" label="color" v-model="color_att_selected"/>
            </v-select>
        </div>
        <div>
            <v-select :items="colormap_items" label="colormap" v-model="colormap_selected"/>
            </v-select>   
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