<template>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12>
          <v-card class="text-xs-center">
            <v-card-title>
              Page Not Found
            </v-card-title>
            <v-card-text>
              <p>Sorry, the page you are looking for does not exist.</p>
            </v-card-text>
            <v-card-actions>
              <v-btn color="primary" to="/">Go to Home</v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </template>
  
  <script>
  export default {
    name: 'NotFound'
  }
  </script>
  
  <style scoped>
  </style>
  